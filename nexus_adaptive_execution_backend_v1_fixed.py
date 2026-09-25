import os
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# ============================================================
# NEXUS ADAPTIVE EXECUTION BACKEND V1
# ============================================================


def cpu_work(seed):
    total = 0

    for i in range(120000):
        value = i + seed
        total += value * value

    return total


def add(a, b):
    return a + b


# ============================================================
# MEMORY
# ============================================================


class BackendStats:

    def __init__(self):
        self.runs = 0
        self.total_time = 0.0
        self.best_time = float("inf")

    @property
    def average_time(self):
        if self.runs == 0:
            return float("inf")

        return self.total_time / self.runs

    def record(self, elapsed):
        self.runs += 1
        self.total_time += elapsed

        if elapsed < self.best_time:
            self.best_time = elapsed


class BackendMemory:

    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.memory = {}

    def key(self, task_count, independent_tasks):
        return (
            task_count,
            independent_tasks
        )

    def candidates(self, independent_tasks):

        limit = min(
            self.max_workers,
            independent_tasks
        )

        candidates = []

        for workers in range(1, limit + 1):

            candidates.append(
                ("THREAD", workers)
            )

            candidates.append(
                ("PROCESS", workers)
            )

        return candidates

    def record(
        self,
        task_count,
        independent_tasks,
        backend,
        workers,
        elapsed
    ):

        key = self.key(
            task_count,
            independent_tasks
        )

        if key not in self.memory:
            self.memory[key] = {}

        configuration = (
            backend,
            workers
        )

        if configuration not in self.memory[key]:

            self.memory[key][configuration] = (
                BackendStats()
            )

        self.memory[key][configuration].record(
            elapsed
        )

    def missing(
        self,
        task_count,
        independent_tasks
    ):

        key = self.key(
            task_count,
            independent_tasks
        )

        known = self.memory.get(
            key,
            {}
        )

        return [
            configuration
            for configuration in self.candidates(
                independent_tasks
            )
            if configuration not in known
        ]

    def best(
        self,
        task_count,
        independent_tasks
    ):

        key = self.key(
            task_count,
            independent_tasks
        )

        known = self.memory.get(
            key,
            {}
        )

        if not known:
            return None

        return min(
            known,
            key=lambda configuration:
                known[configuration].average_time
        )

    def size(self):

        return sum(
            len(pattern)
            for pattern in self.memory.values()
        )


# ============================================================
# BACKEND EXECUTION
# ============================================================


def run_thread_jobs(jobs, workers):

    start = time.perf_counter()

    results = {}

    if workers == 1:

        for task_id, function, args in jobs:

            results[task_id] = function(
                *args
            )

    else:

        with ThreadPoolExecutor(
            max_workers=workers
        ) as executor:

            futures = {}

            for task_id, function, args in jobs:

                futures[task_id] = executor.submit(
                    function,
                    *args
                )

            for task_id, future in futures.items():

                results[task_id] = future.result()

    elapsed = (
        time.perf_counter()
        - start
    )

    return results, elapsed


def run_process_jobs(jobs, workers):

    start = time.perf_counter()

    results = {}

    if workers == 1:

        for task_id, function, args in jobs:

            results[task_id] = function(
                *args
            )

    else:

        with ProcessPoolExecutor(
            max_workers=workers
        ) as executor:

            futures = {}

            for task_id, function, args in jobs:

                futures[task_id] = executor.submit(
                    function,
                    *args
                )

            for task_id, future in futures.items():

                results[task_id] = future.result()

    elapsed = (
        time.perf_counter()
        - start
    )

    return results, elapsed


# ============================================================
# NEXUS ENGINE
# ============================================================


class NexusAdaptiveExecutionBackendV1:

    def __init__(self, max_workers=4):

        self.max_workers = max_workers

        self.memory = BackendMemory(
            max_workers=max_workers
        )

        self.tasks = {}

        self.results = {}

    def add_task(
        self,
        task_id,
        function,
        args=(),
        dependencies=None
    ):

        self.tasks[task_id] = {
            "function": function,
            "args": args,
            "dependencies": dependencies or []
        }

    def reset(self):

        self.results = {}

    def ready_tasks(self):

        ready = []

        for task_id, task in self.tasks.items():

            if task_id in self.results:
                continue

            dependencies = task["dependencies"]

            if all(
                dependency in self.results
                for dependency in dependencies
            ):

                ready.append(task_id)

        return ready

    def build_jobs(self, ready):

        jobs = []

        for task_id in ready:

            task = self.tasks[task_id]

            arguments = list(
                task["args"]
            )

            for dependency in task["dependencies"]:

                arguments.append(
                    self.results[dependency]
                )

            jobs.append(
                (
                    task_id,
                    task["function"],
                    tuple(arguments)
                )
            )

        return jobs

    def execute_backend(
        self,
        ready,
        backend,
        workers
    ):

        jobs = self.build_jobs(
            ready
        )

        if backend == "THREAD":

            return run_thread_jobs(
                jobs,
                workers
            )

        if backend == "PROCESS":

            return run_process_jobs(
                jobs,
                workers
            )

        raise ValueError(
            f"Unknown backend: {backend}"
        )

    def explore(self, ready):

        task_count = len(
            self.tasks
        )

        independent = len(
            ready
        )

        candidates = self.memory.candidates(
            independent
        )

        print()
        print(
            "============================================================"
        )
        print(
            "BACKEND EXPLORATION"
        )
        print(
            "============================================================"
        )

        print(
            f"PATTERN: "
            f"({task_count}, {independent})"
        )

        print()

        measurements = []

        for backend, workers in candidates:

            try:

                values, elapsed = (
                    self.execute_backend(
                        ready,
                        backend,
                        workers
                    )
                )

                measurements.append(
                    {
                        "backend": backend,
                        "workers": workers,
                        "elapsed": elapsed,
                        "values": values,
                        "success": True
                    }
                )

                print(
                    f"{backend:<8}"
                    f"WORKERS={workers} "
                    f"| TIME={elapsed:.6f}s"
                )

            except Exception as error:

                measurements.append(
                    {
                        "backend": backend,
                        "workers": workers,
                        "elapsed": float("inf"),
                        "values": None,
                        "success": False
                    }
                )

                print(
                    f"{backend:<8}"
                    f"WORKERS={workers} "
                    f"| FAILED"
                )

                print(
                    f"           {error}"
                )

        successful = [
            item
            for item in measurements
            if item["success"]
        ]

        if not successful:

            raise RuntimeError(
                "All backend configurations failed."
            )

        best = min(
            successful,
            key=lambda item:
                item["elapsed"]
        )

        print()

        print(
            f"BEST BACKEND: "
            f"{best['backend']}"
        )

        print(
            f"BEST WORKERS: "
            f"{best['workers']}"
        )

        print(
            f"BEST TIME: "
            f"{best['elapsed']:.6f}s"
        )

        for item in successful:

            self.memory.record(
                task_count,
                independent,
                item["backend"],
                item["workers"],
                item["elapsed"]
            )

        return (
            best["backend"],
            best["workers"]
        )

    def execute(self):

        total_start = time.perf_counter()

        executions = 0
        batches = 0

        history = []

        while len(
            self.results
        ) < len(
            self.tasks
        ):

            ready = self.ready_tasks()

            if not ready:

                raise RuntimeError(
                    "No executable tasks available."
                )

            task_count = len(
                self.tasks
            )

            independent = len(
                ready
            )

            missing = self.memory.missing(
                task_count,
                independent
            )

            if missing:

                backend, workers = self.explore(
                    ready
                )

                source = "EXPLORE"

            else:

                backend, workers = self.memory.best(
                    task_count,
                    independent
                )

                source = "EXPLOIT"

            values, elapsed = (
                self.execute_backend(
                    ready,
                    backend,
                    workers
                )
            )

            for task_id, value in values.items():

                self.results[task_id] = value

                executions += 1

            batches += 1

            history.append(
                {
                    "pattern": (
                        task_count,
                        independent
                    ),
                    "backend": backend,
                    "workers": workers,
                    "source": source,
                    "elapsed": elapsed
                }
            )

        total_elapsed = (
            time.perf_counter()
            - total_start
        )

        return {
            "results": dict(
                self.results
            ),
            "elapsed": total_elapsed,
            "executions": executions,
            "batches": batches,
            "history": history
        }


# ============================================================
# ENGINE BUILD
# ============================================================


def build_engine():

    engine = (
        NexusAdaptiveExecutionBackendV1(
            max_workers=4
        )
    )

    # Four independent CPU tasks.
    engine.add_task(
        "A",
        cpu_work,
        args=(1,)
    )

    engine.add_task(
        "B",
        cpu_work,
        args=(2,)
    )

    engine.add_task(
        "C",
        cpu_work,
        args=(3,)
    )

    engine.add_task(
        "D",
        cpu_work,
        args=(4,)
    )

    # Dependency layer.
    engine.add_task(
        "E",
        add,
        dependencies=["A", "B"]
    )

    engine.add_task(
        "F",
        add,
        dependencies=["C", "D"]
    )

    # Final dependency.
    engine.add_task(
        "G",
        add,
        dependencies=["E", "F"]
    )

    return engine


# ============================================================
# VALIDATION
# ============================================================


def validate(results):

    expected_e = (
        results["A"]
        + results["B"]
    )

    expected_f = (
        results["C"]
        + results["D"]
    )

    expected_g = (
        expected_e
        + expected_f
    )

    return (
        results["E"] == expected_e
        and
        results["F"] == expected_f
        and
        results["G"] == expected_g
    )


# ============================================================
# MAIN
# ============================================================


def main():

    print(
        "=== NEXUS ADAPTIVE EXECUTION BACKEND V1 ==="
    )

    print()

    print(
        f"CPU COUNT: {os.cpu_count()}"
    )

    print()

    # One engine is reused so that learning
    # persists between runs.
    engine = build_engine()

    all_correct = True

    for run in range(1, 5):

        engine.reset()

        print()
        print(
            "=" * 75
        )

        print(
            f"RUN {run}"
        )

        print(
            "=" * 75
        )

        result = engine.execute()

        print()

        print(
            f"TOTAL TIME: "
            f"{result['elapsed']:.6f}s"
        )

        print(
            f"EXECUTIONS: "
            f"{result['executions']}"
        )

        print(
            f"BATCHES: "
            f"{result['batches']}"
        )

        print()

        for item in result["history"]:

            print(
                f"PATTERN={item['pattern']} "
                f"| BACKEND={item['backend']} "
                f"| WORKERS={item['workers']} "
                f"| SOURCE={item['source']} "
                f"| TIME={item['elapsed']:.6f}s"
            )

        correct = validate(
            result["results"]
        )

        print()

        print(
            f"CORRECT: {correct}"
        )

        if not correct:

            all_correct = False

    print()
    print(
        "=" * 75
    )

    print(
        "LEARNING MEMORY"
    )

    print(
        "=" * 75
    )

    for key, configurations in sorted(
        engine.memory.memory.items()
    ):

        print()

        print(
            f"PATTERN: {key}"
        )

        for configuration, stats in sorted(
            configurations.items()
        ):

            backend, workers = configuration

            print(
                f"  BACKEND={backend} "
                f"| WORKERS={workers} "
                f"| RUNS={stats.runs} "
                f"| AVG={stats.average_time:.6f}s "
                f"| BEST={stats.best_time:.6f}s"
            )

    print()

    print(
        f"MEMORY ENTRIES: "
        f"{engine.memory.size()}"
    )

    print()

    print(
        f"ALL RESULTS CORRECT: "
        f"{all_correct}"
    )

    print()

    print(
        f"FINAL TEST: "
        f"{all_correct}"
    )


if __name__ == "__main__":
    main()
