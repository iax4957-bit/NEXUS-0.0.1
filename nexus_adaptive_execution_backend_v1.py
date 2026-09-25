import time
import os
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor
)


# ============================================================
# NEXUS ADAPTIVE EXECUTION BACKEND V1
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


# ============================================================
# LEARNING MEMORY
# ============================================================


class NexusBackendMemory:

    def __init__(
        self,
        max_workers=4
    ):

        self.max_workers = max_workers

        self.memory = {}

    def pattern_key(
        self,
        task_count,
        independent_tasks
    ):

        return (
            task_count,
            independent_tasks
        )

    def ensure_pattern(self, key):

        if key not in self.memory:

            self.memory[key] = {}

    def record(
        self,
        task_count,
        independent_tasks,
        backend,
        workers,
        elapsed
    ):

        key = self.pattern_key(
            task_count,
            independent_tasks
        )

        self.ensure_pattern(key)

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

    def candidates(
        self,
        independent_tasks
    ):

        worker_limit = min(
            self.max_workers,
            independent_tasks
        )

        candidates = []

        for workers in range(
            1,
            worker_limit + 1
        ):

            candidates.append(
                ("THREAD", workers)
            )

            candidates.append(
                ("PROCESS", workers)
            )

        return candidates

    def missing(
        self,
        task_count,
        independent_tasks
    ):

        key = self.pattern_key(
            task_count,
            independent_tasks
        )

        self.ensure_pattern(key)

        known = self.memory[key]

        return [
            candidate
            for candidate in self.candidates(
                independent_tasks
            )
            if candidate not in known
        ]

    def best(
        self,
        task_count,
        independent_tasks
    ):

        key = self.pattern_key(
            task_count,
            independent_tasks
        )

        stats = self.memory.get(
            key,
            {}
        )

        if not stats:

            return None

        return min(
            stats,
            key=lambda configuration:
                stats[configuration].average_time
        )

    def memory_size(self):

        return sum(
            len(pattern)
            for pattern in self.memory.values()
        )


# ============================================================
# EXECUTION BACKEND
# ============================================================


def execute_thread_batch(
    functions,
    workers
):

    start = time.perf_counter()

    results = {}

    if workers == 1:

        for task_id, function in functions:

            results[task_id] = function()

    else:

        with ThreadPoolExecutor(
            max_workers=workers
        ) as executor:

            futures = {
                task_id:
                    executor.submit(function)
                for task_id, function in functions
            }

            for task_id, future in futures.items():

                results[task_id] = future.result()

    elapsed = (
        time.perf_counter()
        - start
    )

    return results, elapsed


def execute_process_batch(
    functions,
    workers
):

    start = time.perf_counter()

    results = {}

    if workers == 1:

        for task_id, function in functions:

            results[task_id] = function()

    else:

        with ProcessPoolExecutor(
            max_workers=workers
        ) as executor:

            futures = {
                task_id:
                    executor.submit(function)
                for task_id, function in functions
            }

            for task_id, future in futures.items():

                results[task_id] = future.result()

    elapsed = (
        time.perf_counter()
        - start
    )

    return results, elapsed


# ============================================================
# ADAPTIVE ENGINE
# ============================================================


class NexusAdaptiveExecutionBackendV1:

    def __init__(
        self,
        max_workers=4
    ):

        self.max_workers = max_workers

        self.memory = NexusBackendMemory(
            max_workers=max_workers
        )

        self.tasks = {}

        self.results = {}

    # --------------------------------------------------------
    # TASK MANAGEMENT
    # --------------------------------------------------------

    def add_task(
        self,
        task_id,
        function,
        dependencies=None
    ):

        self.tasks[task_id] = {

            "function": function,

            "dependencies":
                dependencies or []
        }

    def reset(self):

        self.results = {}

    # --------------------------------------------------------
    # READY TASKS
    # --------------------------------------------------------

    def ready_tasks(self):

        ready = []

        for task_id, task in self.tasks.items():

            if task_id in self.results:

                continue

            dependencies = task[
                "dependencies"
            ]

            if all(
                dependency in self.results
                for dependency in dependencies
            ):

                ready.append(task_id)

        return ready

    # --------------------------------------------------------
    # CREATE CALLABLE
    # --------------------------------------------------------

    def create_callable(
        self,
        task_id
    ):

        task = self.tasks[
            task_id
        ]

        function = task[
            "function"
        ]

        dependencies = task[
            "dependencies"
        ]

        arguments = [
            self.results[dependency]
            for dependency in dependencies
        ]

        return (
            function,
            arguments
        )

    # --------------------------------------------------------
    # THREAD EXECUTION
    # --------------------------------------------------------

    def run_thread_task(
        self,
        task_id
    ):

        function, arguments = (
            self.create_callable(
                task_id
            )
        )

        return function(
            *arguments
        )

    # --------------------------------------------------------
    # PROCESS WORKER FUNCTION
    # --------------------------------------------------------

    @staticmethod
    def process_runner(
        function,
        arguments
    ):

        return function(
            *arguments
        )

    # --------------------------------------------------------
    # EXECUTE THREAD
    # --------------------------------------------------------

    def execute_thread(
        self,
        ready,
        workers
    ):

        start = time.perf_counter()

        values = {}

        if workers == 1:

            for task_id in ready:

                values[task_id] = (
                    self.run_thread_task(
                        task_id
                    )
                )

        else:

            with ThreadPoolExecutor(
                max_workers=workers
            ) as executor:

                futures = {}

                for task_id in ready:

                    function, arguments = (
                        self.create_callable(
                            task_id
                        )
                    )

                    futures[task_id] = (
                        executor.submit(
                            function,
                            *arguments
                        )
                    )

                for task_id, future in futures.items():

                    values[task_id] = (
                        future.result()
                    )

        elapsed = (
            time.perf_counter()
            - start
        )

        return values, elapsed

    # --------------------------------------------------------
    # EXECUTE PROCESS
    # --------------------------------------------------------

    def execute_process(
        self,
        ready,
        workers
    ):

        start = time.perf_counter()

        values = {}

        if workers == 1:

            for task_id in ready:

                function, arguments = (
                    self.create_callable(
                        task_id
                    )
                )

                values[task_id] = (
                    function(
                        *arguments
                    )
                )

        else:

            with ProcessPoolExecutor(
                max_workers=workers
            ) as executor:

                futures = {}

                for task_id in ready:

                    function, arguments = (
                        self.create_callable(
                            task_id
                        )
                    )

                    futures[task_id] = (
                        executor.submit(
                            NexusAdaptiveExecutionBackendV1.process_runner,
                            function,
                            arguments
                        )
                    )

                for task_id, future in futures.items():

                    values[task_id] = (
                        future.result()
                    )

        elapsed = (
            time.perf_counter()
            - start
        )

        return values, elapsed

    # --------------------------------------------------------
    # GENERIC EXECUTION
    # --------------------------------------------------------

    def execute_configuration(
        self,
        ready,
        backend,
        workers
    ):

        if backend == "THREAD":

            return self.execute_thread(
                ready,
                workers
            )

        if backend == "PROCESS":

            return self.execute_process(
                ready,
                workers
            )

        raise ValueError(
            f"Unknown backend: {backend}"
        )

    # --------------------------------------------------------
    # EXPLORATION
    # --------------------------------------------------------

    def explore(
        self,
        ready
    ):

        task_count = len(
            self.tasks
        )

        independent = len(
            ready
        )

        candidates = (
            self.memory.candidates(
                independent
            )
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

        original_results = dict(
            self.results
        )

        for backend, workers in candidates:

            self.results = dict(
                original_results
            )

            try:

                values, elapsed = (
                    self.execute_configuration(
                        ready,
                        backend,
                        workers
                    )
                )

                measurements.append({
                    "backend": backend,
                    "workers": workers,
                    "elapsed": elapsed,
                    "values": values,
                    "success": True
                })

                print(
                    f"{backend:<7} "
                    f"WORKERS={workers} "
                    f"| TIME={elapsed:.6f}s"
                )

            except Exception as error:

                measurements.append({
                    "backend": backend,
                    "workers": workers,
                    "elapsed": float("inf"),
                    "values": None,
                    "success": False,
                    "error": str(error)
                })

                print(
                    f"{backend:<7} "
                    f"WORKERS={workers} "
                    f"| FAILED"
                )

                print(
                    f"         {error}"
                )

        self.results = dict(
            original_results
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

        best_backend = best[
            "backend"
        ]

        best_workers = best[
            "workers"
        ]

        best_time = best[
            "elapsed"
        ]

        print()

        print(
            f"BEST BACKEND: "
            f"{best_backend}"
        )

        print(
            f"BEST WORKERS: "
            f"{best_workers}"
        )

        print(
            f"BEST TIME: "
            f"{best_time:.6f}s"
        )

        print()

        for item in measurements:

            if item["success"]:

                self.memory.record(
                    task_count,
                    independent,
                    item["backend"],
                    item["workers"],
                    item["elapsed"]
                )

        return (
            best_backend,
            best_workers
        )

    # --------------------------------------------------------
    # MAIN EXECUTION
    # --------------------------------------------------------

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

            missing = (
                self.memory.missing(
                    task_count,
                    independent
                )
            )

            if missing:

                backend, workers = (
                    self.explore(
                        ready
                    )
                )

                source = "EXPLORE"

            else:

                configuration = (
                    self.memory.best(
                        task_count,
                        independent
                    )
                )

                backend, workers = (
                    configuration
                )

                source = "EXPLOIT"

            values, elapsed = (
                self.execute_configuration(
                    ready,
                    backend,
                    workers
                )
            )

            for task_id, value in values.items():

                self.results[
                    task_id
                ] = value

                executions += 1

            batches += 1

            history.append({

                "pattern":
                    (
                        task_count,
                        independent
                    ),

                "backend":
                    backend,

                "workers":
                    workers,

                "source":
                    source,

                "elapsed":
                    elapsed
            })

        total_elapsed = (
            time.perf_counter()
            - total_start
        )

        return {

            "results":
                dict(self.results),

            "elapsed":
                total_elapsed,

            "executions":
                executions,

            "batches":
                batches,

            "history":
                history
        }


# ============================================================
# CPU WORK
# ============================================================


def cpu_work(seed):

    total = 0

    for i in range(
        100000
    ):

        value = (
            i + seed
        )

        total += (
            value * value
        )

    return total


# ============================================================
# DEPENDENCY FUNCTIONS
# ============================================================


def add(
    a,
    b
):

    return a + b


# ============================================================
# TEST
# ============================================================


def build_engine():

    engine = (
        NexusAdaptiveExecutionBackendV1(
            max_workers=4
        )
    )

    engine.add_task(
        "A",
        cpu_work,
        []
    )

    engine.add_task(
        "B",
        cpu_work,
        []
    )

    engine.add_task(
        "C",
        cpu_work,
        []
    )

    engine.add_task(
        "D",
        cpu_work,
        []
    )

    engine.add_task(
        "E",
        add,
        ["A", "B"]
    )

    engine.add_task(
        "F",
        add,
        ["C", "D"]
    )

    engine.add_task(
        "G",
        add,
        ["E", "F"]
    )

    return engine


# ============================================================
# MAIN
# ============================================================


def main():

    print(
        "=== NEXUS ADAPTIVE EXECUTION BACKEND V1 ==="
    )

    print()

    print(
        f"CPU COUNT: "
        f"{os.cpu_count()}"
    )

    print()

    total_runs = 4

    all_correct = True

    final_engine = None

    for run in range(
        1,
        total_runs + 1
    ):

        engine = build_engine()

        final_engine = engine

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

        for item in result[
            "history"
        ]:

            print(
                f"PATTERN={item['pattern']} "
                f"| BACKEND={item['backend']} "
                f"| WORKERS={item['workers']} "
                f"| SOURCE={item['source']} "
                f"| TIME={item['elapsed']:.6f}s"
            )

        results = result[
            "results"
        ]

        expected_e = (
            results["A"]
            + results[
