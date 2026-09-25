import os
import sys
import json
import time
import statistics
import hashlib
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


VERSION = "NEXUS UNIFIED V2"
MEMORY_FILE = "nexus_unified_v2_memory.json"


# ============================================================
# WORK FUNCTIONS
# ============================================================

def cpu_work(value, rounds=80000):
    x = int(value) + 1

    for i in range(rounds):
        x = (
            x * 1664525
            + 1013904223
            + i
        ) & 0xFFFFFFFF

    return x


def add_values(a, b):
    return a + b


def multiply_values(a, b):
    return a * b


FUNCTIONS = {
    "cpu": cpu_work,
    "add": add_values,
    "multiply": multiply_values,
}


# ============================================================
# TASK
# ============================================================

@dataclass
class Task:
    task_id: str
    operation: str
    args: tuple
    dependencies: tuple = ()
    cache_key: str = ""


# ============================================================
# WORK GRAPH
# ============================================================

class WorkGraph:

    def __init__(self):
        self.tasks = {}

    def add(self, task):
        if task.task_id in self.tasks:
            raise ValueError(
                f"Duplicate task: {task.task_id}"
            )

        self.tasks[task.task_id] = task

    def validate(self):
        for task in self.tasks.values():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise ValueError(
                        f"Missing dependency: {dep}"
                    )

        visiting = set()
        visited = set()

        def visit(task_id):
            if task_id in visiting:
                raise ValueError(
                    f"Cycle detected: {task_id}"
                )

            if task_id in visited:
                return

            visiting.add(task_id)

            for dep in self.tasks[
                task_id
            ].dependencies:
                visit(dep)

            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in self.tasks:
            visit(task_id)

        return True

    def ready(self, completed):
        result = []

        for task in self.tasks.values():
            if task.task_id in completed:
                continue

            if all(
                dep in completed
                for dep in task.dependencies
            ):
                result.append(task)

        return result# ============================================================
# RESULT CACHE
# ============================================================

class ResultCache:

    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def has(self, key):
        return key in self.data

    def put(self, key, value):
        self.data[key] = value

    def clear(self):
        self.data.clear()

    def __len__(self):
        return len(self.data)


# ============================================================
# LEARNING MEMORY
# ============================================================

@dataclass
class MemoryEntry:
    backend: str
    workers: int
    avg_time: float
    runs: int
    successes: int
    failures: int

    @property
    def reliability(self):
        total = (
            self.successes
            + self.failures
        )

        if total == 0:
            return 0.0

        return (
            self.successes / total
        )


class LearningMemory:

    def __init__(
        self,
        filename=MEMORY_FILE,
    ):
        self.filename = filename
        self.data = {}
        self.load()

    def make_key(
        self,
        pattern,
        workload,
        backend,
        workers,
    ):
        return (
            f"{pattern[0]}:"
            f"{pattern[1]}:"
            f"{workload}:"
            f"{backend}:"
            f"{workers}"
        )

    def load(self):
        if not os.path.exists(
            self.filename
        ):
            return

        try:
            with open(
                self.filename,
                "r",
                encoding="utf-8",
            ) as f:
                raw = json.load(f)

            for key, value in raw.items():
                self.data[key] = MemoryEntry(
                    backend=value["backend"],
                    workers=value["workers"],
                    avg_time=value["avg_time"],
                    runs=value["runs"],
                    successes=value["successes"],
                    failures=value["failures"],
                )

        except Exception:
            self.data = {}

    def save(self):
        raw = {}

        for key, entry in self.data.items():
            raw[key] = asdict(entry)

        temporary = (
            self.filename
            + ".tmp"
        )

        with open(
            temporary,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                raw,
                f,
                indent=2,
            )

        os.replace(
            temporary,
            self.filename,
        )

    def record(
        self,
        pattern,
        workload,
        backend,
        workers,
        elapsed,
        success,
    ):
        key = self.make_key(
            pattern,
            workload,
            backend,
            workers,
        )

        old = self.data.get(key)

        if old is None:
            self.data[key] = MemoryEntry(
                backend=backend,
                workers=workers,
                avg_time=elapsed,
                runs=1,
                successes=(
                    1 if success else 0
                ),
                failures=(
                    0 if success else 1
                ),
            )
            self.save()
            return

        old.avg_time = (
            (
                old.avg_time
                * old.runs
            )
            + elapsed
        ) / (old.runs + 1)

        old.runs += 1

        if success:
            old.successes += 1
        else:
            old.failures += 1

        self.save()

    def choose(
        self,
        pattern,
        workload,
    ):
        candidates = []

        pattern_prefix = (
            f"{pattern[0]}:"
            f"{pattern[1]}:"
            f"{workload}:"
        )

        for key, entry in self.data.items():
            if not key.startswith(
                pattern_prefix
            ):
                continue

            if entry.reliability >= 0.50:
                candidates.append(entry)

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: (
                item.avg_time,
                -item.reliability,
                -item.runs,
            )
        )

        return candidates[0]

    def print_memory(self):
        print()
        print("LEARNING MEMORY")
        print("-" * 70)

        if not self.data:
            print("EMPTY")
            return

        entries = list(
            self.data.values()
        )

        entries.sort(
            key=lambda item: (
                item.backend,
                item.workers,
                item.avg_time,
            )
        )

        for entry in entries:
            print(
                f"{entry.backend:<7} "
                f"W={entry.workers:<2} "
                f"TIME={entry.avg_time:.6f}s "
                f"RUNS={entry.runs:<3} "
                f"REL={entry.reliability:.2f}"
            )

        print(
            f"ENTRIES: {len(entries)}"
        )# ============================================================
# BACKEND EXECUTION
# ============================================================

def execute_job(job):
    operation, args = job

    function = FUNCTIONS[
        operation
    ]

    return function(*args)


def execute_threads(
    jobs,
    workers,
):
    if not jobs:
        return {}

    workers = max(
        1,
        min(
            workers,
            len(jobs),
        ),
    )

    results = {}

    with ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = []

        for (
            task_id,
            operation,
            args,
        ) in jobs:

            future = executor.submit(
                execute_job,
                (
                    operation,
                    args,
                ),
            )

            futures.append(
                (
                    task_id,
                    future,
                )
            )

        for (
            task_id,
            future,
        ) in futures:

            results[
                task_id
            ] = future.result()

    return results


def execute_processes(
    jobs,
    workers,
):
    if not jobs:
        return {}

    workers = max(
        1,
        min(
            workers,
            len(jobs),
        ),
    )

    results = {}

    with ProcessPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = []

        for (
            task_id,
            operation,
            args,
        ) in jobs:

            future = executor.submit(
                execute_job,
                (
                    operation,
                    args,
                ),
            )

            futures.append(
                (
                    task_id,
                    future,
                )
            )

        for (
            task_id,
            future,
        ) in futures:

            results[
                task_id
            ] = future.result()

    return results


# ============================================================
# NEXUS ENGINE
# ============================================================

class NexusUnifiedV2:

    def __init__(
        self,
        max_workers=None,
        exploration_repeats=2,
    ):
        self.cpu_count = (
            os.cpu_count() or 1
        )

        if max_workers is None:
            max_workers = min(
                self.cpu_count,
                4,
            )

        self.max_workers = max(
            1,
            max_workers,
        )

        self.exploration_repeats = max(
            1,
            exploration_repeats,
        )

        self.graph = WorkGraph()
        self.cache = ResultCache()
        self.memory = LearningMemory()

        self.results = {}

        self.execution_count = 0
        self.cache_hits = 0
        self.batch_count = 0    # ========================================================
    # TASK MANAGEMENT
    # ========================================================

    def add_task(
        self,
        task_id,
        operation,
        args=(),
        dependencies=(),
    ):
        task = Task(
            task_id=task_id,
            operation=operation,
            args=tuple(args),
            dependencies=tuple(
                dependencies
            ),
        )

        task.cache_key = (
            self.make_cache_key(
                operation,
                task.args,
            )
        )

        self.graph.add(task)

    def make_cache_key(
        self,
        operation,
        args,
    ):
        raw = repr(
            (
                operation,
                args,
            )
        )

        return hashlib.sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()

    # ========================================================
    # DEPENDENCY ARGUMENTS
    # ========================================================

    def resolve_arg(self, arg):

        if (
            isinstance(arg, tuple)
            and len(arg) == 2
            and arg[0] == "$"
        ):
            task_id = arg[1]

            if task_id not in self.results:
                raise RuntimeError(
                    f"Missing result: "
                    f"{task_id}"
                )

            return self.results[
                task_id
            ]

        return arg

    def resolve_args(self, task):
        return tuple(
            self.resolve_arg(arg)
            for arg in task.args
        )

    # ========================================================
    # JOB BUILDING
    # ========================================================

    def build_jobs(self, tasks):
        jobs = []

        for task in tasks:

            args = self.resolve_args(
                task
            )

            cache_key = (
                self.make_cache_key(
                    task.operation,
                    args,
                )
            )

            if self.cache.has(
                cache_key
            ):
                self.results[
                    task.task_id
                ] = self.cache.get(
                    cache_key
                )

                self.cache_hits += 1

                continue

            jobs.append(
                (
                    task.task_id,
                    task.operation,
                    args,
                )
            )

        return jobs

    # ========================================================
    # CANDIDATE EXECUTION
    # ========================================================

    def execute_candidate(
        self,
        jobs,
        backend,
        workers,
    ):
        start = time.perf_counter()

        try:

            if backend == "THREAD":
                results = execute_threads(
                    jobs,
                    workers,
                )

            elif backend == "PROCESS":
                results = execute_processes(
                    jobs,
                    workers,
                )

            else:
                raise ValueError(
                    f"Unknown backend: "
                    f"{backend}"
                )

            elapsed = (
                time.perf_counter()
                - start
            )

            return (
                results,
                elapsed,
                True,
            )

        except Exception as exc:

            elapsed = (
                time.perf_counter()
                - start
            )

            print(
                f"BACKEND FAILURE: "
                f"{backend} "
                f"x{workers} "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            return (
                {},
                elapsed,
                False,
            )

    # ========================================================
    # PATTERN
    # ========================================================

    def get_pattern(
        self,
        tasks,
    ):
        return (
            len(tasks),
            sum(
                len(
                    task.dependencies
                )
                for task in tasks
            ),
        )
    
    def get_workload(
        self,
        jobs,
    ):
        if not jobs:
            return 0

        operations = {
            job[1]
            for job in jobs
        }

        if operations == {"game"}:
            return jobs[0][2][0]

        return 0

    # ========================================================
    # EXPLORE
    # ========================================================

    def explore(
        self,
        jobs,
        pattern,
        workload,
    ):
        candidates = []

        worker_limit = min(
            self.max_workers,
            max(
                1,
                len(jobs),
            ),
        )

        for backend in (
            "THREAD",
            "PROCESS",
        ):
            for workers in range(
                1,
                worker_limit + 1,
            ):
                candidates.append(
                    (
                        backend,
                        workers,
                    )
                )

        print()
        print("MODE: EXPLORE")
        print(
            f"PATTERN: {pattern}"
        )

        best = None

        for (
            backend,
            workers,
        ) in candidates:

            times = []
            best_results = {}

            for _ in range(
                self.exploration_repeats
            ):

                (
                    results,
                    elapsed,
                    success,
                ) = self.execute_candidate(
                    jobs,
                    backend,
                    workers,
                )

                self.memory.record(
                    pattern,
                    workload,
                    backend,
                    workers,
                    elapsed,
                    success,
                )

                if success:
                    times.append(
                        elapsed
                    )

                    best_results = results

            if not times:
                continue

            average = statistics.mean(
                times
            )

            print(
                f"{backend:<7} "
                f"W={workers} "
                f"AVG={average:.6f}s"
            )

            if (
                best is None
                or average < best[
                    "time"
                ]
            ):
                best = {
                    "backend": backend,
                    "workers": workers,
                    "time": average,
                    "results": best_results,
                }

        if best is None:
            raise RuntimeError(
                "All candidates failed."
            )

        print(
            f"BEST: "
            f"{best['backend']} "
            f"x{best['workers']} "
            f"{best['time']:.6f}s"
        )

        return best

    # ========================================================
    # EXPLOIT
    # ========================================================

    def exploit(
        self,
        jobs,
        pattern,
        workload,
        learned,
    ):
        print()
        print("MODE: EXPLOIT")

        print(
            f"PATTERN: {pattern}"
        )

        print(
            f"LEARNED: "
            f"{learned.backend} "
            f"x{learned.workers}"
        )

        (
            results,
            elapsed,
            success,
        ) = self.execute_candidate(
            jobs,
            learned.backend,
            learned.workers,
        )

        self.memory.record(
            pattern,
            workload,
            learned.backend,
            learned.workers,
            elapsed,
            success,
        )

        if success:
            print(
                f"TIME: {elapsed:.6f}s"
            )

            return {
                "backend": learned.backend,
                "workers": learned.workers,
                "time": elapsed,
                "results": results,
            }

        print(
            "LEARNED STRATEGY FAILED"
        )

        # ====================================================
        # FALLBACK
        # ====================================================

        if learned.backend == "PROCESS":

            fallback_backend = "THREAD"

            print(
                f"FALLBACK: "
                f"{fallback_backend} "
                f"x{learned.workers}"
            )

            (
                fallback_results,
                fallback_elapsed,
                fallback_success,
            ) = self.execute_candidate(
                jobs,
                fallback_backend,
                learned.workers,
            )

            self.memory.record(
                pattern,
                fallback_backend,
                learned.workers,
                fallback_elapsed,
                fallback_success,
            )

            if fallback_success:

                print(
                    f"FALLBACK SUCCESS: "
                    f"{fallback_backend} "
                    f"x{learned.workers} "
                    f"{fallback_elapsed:.6f}s"
                )

                return {
                    "backend": fallback_backend,
                    "workers": learned.workers,
                    "time": fallback_elapsed,
                    "results": fallback_results,
                }

            print(
                "FALLBACK FAILED"
            )

        return None

    # ========================================================
    # STORE RESULTS
    # ========================================================

    def store_results(
        self,
        results,
    ):
        for (
            task_id,
            value,
        ) in results.items():

            self.results[
                task_id
            ] = value

            task = self.graph.tasks[
                task_id
            ]

            args = self.resolve_args(
                task
            )

            cache_key = (
                self.make_cache_key(
                    task.operation,
                    args,
                )
            )

            self.cache.put(
                cache_key,
                value,
            )

            self.execution_count += 1    # ========================================================
    # MAIN EXECUTION LOOP
    # ========================================================

    def run(self):

        self.graph.validate()

        completed = set()

        total_tasks = len(
            self.graph.tasks
        )

        while len(completed) < total_tasks:

            ready = self.graph.ready(
                completed
            )

            if not ready:
                raise RuntimeError(
                    "No ready tasks."
                )

            jobs = self.build_jobs(
                ready
            )

            self.batch_count += 1

            # Everything came from cache.
            if not jobs:

                for task in ready:
                    completed.add(
                        task.task_id
                    )

                continue

            pattern = self.get_pattern(
                ready
            )

            workload = self.get_workload(
                jobs
            )

            learned = self.memory.choose(
                pattern,
                workload,
            )

            result = None

            if learned is not None:
                result = self.exploit(
                    jobs,
                    pattern,
                    workload,
                    learned,
                )

            if result is None:
                result = self.explore(
                    jobs,
                    pattern,
                    workload,
                )

            self.store_results(
                result["results"]
            )

            for task in ready:
                completed.add(
                    task.task_id
                )

        return dict(
            self.results
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_results(self):

        required = (
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
        )

        for task_id in required:
            if task_id not in self.results:
                return False

        if self.results["E"] != (
            self.results["A"]
            + self.results["B"]
        ):
            return False

        if self.results["F"] != (
            self.results["C"]
            + self.results["D"]
        ):
            return False

        if self.results["G"] != (
            self.results["E"]
            + self.results["F"]
        ):
            return False

        if self.results["H"] != (
            self.results["G"] * 2
        ):
            return False

        return True

    # ========================================================
    # REPORT
    # ========================================================

    def report(self):
        print()
        print(
            "EXECUTIONS:",
            self.execution_count,
        )

        print(
            "CACHE HITS:",
            self.cache_hits,
        )

        print(
            "BATCHES:",
            self.batch_count,
        )

        print(
            "CACHE SIZE:",
            len(self.cache),
        )

        print(
            "RESULTS:",
            len(self.results),
        )

        print(
            "CORRECT:",
            self.validate_results(),
        )


# ============================================================
# BUILD NEXUS GRAPH
# ============================================================

def build_nexus():

    engine = NexusUnifiedV2(
        max_workers=4,
        exploration_repeats=2,
    )

    engine.add_task(
        "A",
        "cpu",
        (1, 80000),
    )

    engine.add_task(
        "B",
        "cpu",
        (2, 80000),
    )

    engine.add_task(
        "C",
        "cpu",
        (3, 80000),
    )

    engine.add_task(
        "D",
        "cpu",
        (4, 80000),
    )

    engine.add_task(
        "E",
        "add",
        (
            ("$", "A"),
            ("$", "B"),
        ),
        (
            "A",
            "B",
        ),
    )

    engine.add_task(
        "F",
        "add",
        (
            ("$", "C"),
            ("$", "D"),
        ),
        (
            "C",
            "D",
        ),
    )
    engine.add_task(
        "G",
        "add",
        (
            ("$", "E"),
            ("$", "F"),
        ),
        (
            "E",
            "F",
        ),
    )

    engine.add_task(
        "H",
        "multiply",
        (
            ("$", "G"),
            2,
        ),
        (
            "G",
        ),
    )

    # Same calculation as A.
    # This intentionally tests cache reuse.
    engine.add_task(
        "I",
        "cpu",
        (1, 80000),
        (
            "A",
        ),
    )

    return engine


# ============================================================
# SELF TESTS
# ============================================================

def test_basic_functions():

    assert add_values(
        2,
        3,
    ) == 5

    assert multiply_values(
        4,
        5,
    ) == 20

    first = cpu_work(
        1,
        1000,
    )

    second = cpu_work(
        1,
        1000,
    )

    assert first == second

    print(
        "TEST BASIC FUNCTIONS: PASS"
    )


def test_graph():

    graph = WorkGraph()

    graph.add(
        Task(
            "A",
            "cpu",
            (1,),
        )
    )

    graph.add(
        Task(
            "B",
            "add",
            (
                ("$", "A"),
                1,
            ),
            (
                "A",
            ),
        )
    )

    assert graph.validate()

    ready = graph.ready(
        set()
    )

    assert len(ready) == 1

    assert (
        ready[0].task_id
        == "A"
    )

    print(
        "TEST WORK GRAPH: PASS"
    )


def test_cache():

    cache = ResultCache()

    cache.put(
        "test",
        123,
    )

    assert cache.has(
        "test"
    )

    assert cache.get(
        "test"
    ) == 123

    print(
        "TEST CACHE: PASS"
    )


def test_thread_backend():

    jobs = [
        (
            "A",
            "add",
            (2, 3),
        ),
        (
            "B",
            "multiply",
            (4, 5),
        ),
    ]

    results = execute_threads(
        jobs,
        2,
    )

    assert results["A"] == 5
    assert results["B"] == 20

    print(
        "TEST THREAD BACKEND: PASS"
    )


def test_process_backend():

    jobs = [
        (
            "A",
            "add",
            (2, 3),
        ),
        (
            "B",
            "multiply",
            (4, 5),
        ),
    ]

    results = execute_processes(
        jobs,
        2,
    )

    assert results["A"] == 5
    assert results["B"] == 20

    print(
        "TEST PROCESS BACKEND: PASS"
    )
def test_unified_engine():

    engine = build_nexus()

    results = engine.run()

    assert len(results) == 9

    assert engine.validate_results()

    # I must equal A because it is
    # exactly the same CPU calculation.
    assert (
        results["I"]
        == results["A"]
    )

    assert engine.cache_hits >= 1

    print(
        "TEST UNIFIED ENGINE: PASS"
    )


def run_self_tests():

    print()
    print("=" * 70)
    print("NEXUS SELF TESTS")
    print("=" * 70)

    test_basic_functions()
    test_graph()
    test_cache()
    test_thread_backend()
    test_process_backend()
    test_unified_engine()

    print()
    print(
        "ALL SELF TESTS: PASS"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print(VERSION)
    print("=" * 70)

    print(
        "PYTHON:",
        sys.version.split()[0],
    )

    print(
        "CPU COUNT:",
        os.cpu_count() or 1,
    )

    print(
        "MAX WORKERS:",
        min(
            os.cpu_count() or 1,
            4,
        ),
    )

    run_self_tests()

    print()
    print("=" * 70)
    print("NEXUS ADAPTIVE EXECUTION")
    print("=" * 70)

    all_correct = True

    for run_number in range(
        1,
        4,
    ):

        print()
        print(
            f"RUN {run_number}"
        )

        engine = build_nexus()

        try:

            engine.run()

            correct = (
                engine.validate_results()
            )

            all_correct = (
                all_correct
                and correct
            )

            engine.report()

        except Exception as exc:

            all_correct = False

            print(
                "RUN FAILED"
            )

            print(
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            break

    memory = LearningMemory()

    memory.print_memory()

    print()
    print("=" * 70)

    print(
        "ALL RESULTS CORRECT:",
        all_correct,
    )

    print(
        "FINAL TEST:",
        "PASS"
        if all_correct
        else "FAIL",
    )

    print("=" * 70)

    return (
        0
        if all_correct
        else 1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(main())
