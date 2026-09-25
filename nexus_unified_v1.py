import os
import sys
import json
import time
import math
import statistics
import hashlib
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# ============================================================
# NEXUS UNIFIED V1
# ============================================================

VERSION = "NEXUS UNIFIED V1.0"
MEMORY_FILE = "nexus_unified_memory_v1.json"


# ============================================================
# BASIC WORK FUNCTIONS
# ============================================================

def cpu_work(value, rounds=120_000):
    """
    Deterministic CPU workload.
    The function is top-level so it can be used by ProcessPoolExecutor.
    """
    x = int(value) + 1

    for i in range(rounds):
        x = (x * 1664525 + 1013904223 + i) & 0xFFFFFFFF

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
                f"Duplicate task ID: {task.task_id}"
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
                    f"Dependency cycle detected at {task_id}"
                )

            if task_id in visited:
                return

            visiting.add(task_id)

            for dep in self.tasks[task_id].dependencies:
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

        return result


# ============================================================
# CACHE
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
        total = self.successes + self.failures

        if total == 0:
            return 0.0

        return self.successes / total


class LearningMemory:

    def __init__(self, filename=MEMORY_FILE):
        self.filename = filename
        self.data = {}

        self.load()

    def key(self, pattern, backend, workers):
        return (
            f"{pattern[0]}:{pattern[1]}:"
            f"{backend}:{workers}"
        )

    def load(self):
        if not os.path.exists(self.filename):
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

        temp = self.filename + ".tmp"

        with open(
            temp,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                raw,
                f,
                indent=2,
            )

        os.replace(
            temp,
            self.filename,
        )

    def record(
        self,
        pattern,
        backend,
        workers,
        elapsed,
        success,
    ):
        key = self.key(
            pattern,
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
                successes=1 if success else 0,
                failures=0 if success else 1,
            )
        else:
            old.avg_time = (
                old.avg_time * old.runs
                + elapsed
            ) / (old.runs + 1)

            old.runs += 1

            if success:
                old.successes += 1
            else:
                old.failures += 1

        self.save()

    def candidates(self, pattern):
        result = []

        for entry in self.data.values():

            if entry.runs < 1:
                continue

            result.append(entry)

        return result

    def choose(self, pattern):
        candidates = self.candidates(pattern)

        if not candidates:
            return None

        candidates = [
            e for e in candidates
            if e.reliability >= 0.50
        ]

        if not candidates:
            return None

        candidates.sort(
            key=lambda e: (
                e.avg_time,
                -e.reliability,
                -e.runs,
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

        entries = sorted(
            self.data.values(),
            key=lambda e: (
                e.backend,
                e.workers,
                e.avg_time,
            ),
        )

        for entry in entries:
            print(
                f"{entry.backend:<7} "
                f"workers={entry.workers:<2} "
                f"time={entry.avg_time:.6f}s "
                f"runs={entry.runs:<3} "
                f"reliability={entry.reliability:.2f}"
            )

        print(
            f"MEMORY ENTRIES: {len(entries)}"
        )


# ============================================================
# PROCESS / THREAD EXECUTION
# ============================================================

def execute_job(job):
    operation, args = job

    fn = FUNCTIONS[operation]

    return fn(*args)


def execute_threads(jobs, workers):
    if not jobs:
        return {}

    workers = max(
        1,
        min(workers, len(jobs)),
    )

    results = {}

    with ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = []

        for task_id, operation, args in jobs:
            futures.append(
                (
                    task_id,
                    executor.submit(
                        execute_job,
                        (operation, args),
                    ),
                )
            )

        for task_id, future in futures:
            results[task_id] = future.result()

    return results


def execute_processes(jobs, workers):
    if not jobs:
        return {}

    workers = max(
        1,
        min(workers, len(jobs)),
    )

    results = {}

    with ProcessPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = []

        for task_id, operation, args in jobs:
            futures.append(
                (
                    task_id,
                    executor.submit(
                        execute_job,
                        (operation, args),
                    ),
                )
            )

        for task_id, future in futures:
            results[task_id] = future.result()

    return results


# ============================================================
# UNIFIED ENGINE
# ============================================================

class NexusUnifiedV1:

    def __init__(
        self,
        max_workers=None,
        exploration_repeats=2,
    ):
        self.cpu_count = os.cpu_count() or 1

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
        self.batch_count = 0

    # --------------------------------------------------------
    # TASK CREATION
    # --------------------------------------------------------

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
            dependencies=tuple(dependencies),
        )

        task.cache_key = self.make_cache_key(
            operation,
            task.args,
        )

        self.graph.add(task)

    # --------------------------------------------------------
    # CACHE KEY
    # --------------------------------------------------------

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
            raw.encode("utf-8")
        ).hexdigest()

    # --------------------------------------------------------
    # ARG RESOLUTION
    # --------------------------------------------------------

    def resolve_arg(
        self,
        arg,
    ):
        if (
            isinstance(arg, tuple)
            and len(arg) == 2
            and arg[0] == "$"
        ):
            task_id = arg[1]

            if task_id not in self.results:
                raise RuntimeError(
                    f"Missing result: {task_id}"
                )

            return self.results[task_id]

        return arg

    def resolve_args(self, task):
        return tuple(
            self.resolve_arg(arg)
            for arg in task.args
        )

    # --------------------------------------------------------
    # BUILD JOBS
    # --------------------------------------------------------

    def build_jobs(self, tasks):
        jobs = []

        for task in tasks:

            args = self.resolve_args(task)

            cache_key = self.make_cache_key(
                task.operation,
                args,
            )

            if self.cache.has(cache_key):
                value = self.cache.get(cache_key)

                self.results[
                    task.task_id
                ] = value

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

    # --------------------------------------------------------
    # EXECUTE ONE CANDIDATE
    # --------------------------------------------------------

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
                    f"Unknown backend: {backend}"
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
                f"{backend} x{workers} "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            return (
                {},
                elapsed,
                False,
            )

    # --------------------------------------------------------
    # PATTERN
    # --------------------------------------------------------

    def pattern(self, tasks):
        return (
            len(tasks),
            sum(
                len(task.dependencies)
                for task in tasks
            ),
        )

    # --------------------------------------------------------
    # EXPLORE
    # --------------------------------------------------------

    def explore(
        self,
        jobs,
        pattern,
    ):
        candidate_list = []

        worker_limit = min(
            self.max_workers,
            max(1, len(jobs)),
        )

        for backend in (
            "THREAD",
            "PROCESS",
        ):
            for workers in range(
                1,
                worker_limit + 1,
            ):
                candidate_list.append(
                    (
                        backend,
                        workers,
                    )
                )

        print()
        print("EXPLORE")
        print(
            f"PATTERN: {pattern}"
        )
        print(
            f"CANDIDATES: "
            f"{len(candidate_list)}"
        )

        best = None

        for backend, workers in candidate_list:

            times = []
            final_results = {}

            for _ in range(
                self.exploration_repeats
            ):

                (
                    candidate_results,
                    elapsed,
                    success,
                ) = self.execute_candidate(
                    jobs,
                    backend,
                    workers,
                )

                self.memory.record(
                    pattern,
                    backend,
                    workers,
                    elapsed,
                    success,
                )

                if success:
                    times.append(
                        elapsed
                    )
                    final_results = (
                        candidate_results
                    )

            if not times:
                continue

            avg = statistics.mean(
                times
            )

            print(
                f"{backend:<7} "
                f"workers={workers} "
                f"avg={avg:.6f}s"
            )

            if (
                best is None
                or avg < best["time"]
            ):
                best = {
                    "backend": backend,
                    "workers": workers,
                    "time": avg,
                    "results": final_results,
                }

        if best is None:
            raise RuntimeError(
                "All execution candidates failed."
            )

        print(
            f"BEST: "
            f"{best['backend']} "
            f"x{best['workers']} "
            f"{best['time']:.6f}s"
        )

        return best

    # --------------------------------------------------------
    # EXPLOIT
    # --------------------------------------------------------

    def exploit(
        self,
        jobs,
        pattern,
        learned,
    ):
        print()
        print("EXPLOIT")
        print(
            f"PATTERN: {pattern}"
        )
        print(
            f"LEARNED: "
            f"{learned.backend} "
            f"x{learned.workers} "
            f"avg={learned.avg_time:.6f}s "
            f"reliability={learned.reliability:.2f}"
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
            learned.backend,
            learned.workers,
            elapsed,
            success,
        )

        if success:
            return {
                "backend": learned.backend,
                "workers": learned.workers,
                "time": elapsed,
                "results": results,
            }

        print(
            "LEARNED STRATEGY FAILED"
        )

        return None

    # --------------------------------------------------------
    # STORE RESULTS
    # --------------------------------------------------------

    def store_results(
        self,
        tasks,
        results,
    ):
        for task_id, value in results.items():

            self.results[task_id] = value

            task = self.graph.tasks[
                task_id
            ]

            args = self.resolve_args(task)

            cache_key = self.make_cache_key(
                task.operation,
                args,
            )

            self.cache.put(
                cache_key,
                value,
            )

            self.execution_count += 1

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(self):

        self.graph.validate()

        completed = set()

        while len(completed) < len(
            self.graph.tasks
        ):

            ready = self.graph.ready(
                completed
            )

            if not ready:
                raise RuntimeError(
                    "No ready tasks. "
                    "Graph may contain a cycle."
                )

            jobs = self.build_jobs(
                ready
            )

            self.batch_count += 1

            # All tasks were satisfied from cache.
            if not jobs:

                for task in ready:
                    completed.add(
                        task.task_id
                    )

                continue

            pattern = self.pattern(
                ready
            )

            learned = self.memory.choose(
                pattern
            )

            result = None

            if learned is not None:
                result = self.exploit(
                    jobs,
                    pattern,
                    learned,
                )

            if result is None:
                result = self.explore(
                result = self.explore(
                    jobs,
                    pattern,
                )

            self.store_results(
                ready,
                result["results"],
            )

            for task in ready:
                completed.add(
                    task.task_id
                )

        return dict(self.results)

    def validate_results(self):
        expected = {
            "A": self.results.get("A"),
            "B": self.results.get("B"),
            "C": self.results.get("C"),
            "D": self.results.get("D"),
        }

        if any(
            value is None
            for value in expected.values()
        ):
            return False

        if self.results.get("E") != (
            self.results["A"]
            + self.results["B"]
        ):
            return False

        if self.results.get("F") != (
            self.results["C"]
            + self.results["D"]
        ):
            return False

        if self.results.get("G") != (
            self.results["E"]
            + self.results["F"]
        ):
            return False

        if self.results.get("H") != (
            self.results["G"] * 2
        ):
            return False

        return True
