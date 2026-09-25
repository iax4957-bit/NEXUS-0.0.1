import time
from concurrent.futures import ThreadPoolExecutor


class WorkerStats:

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


class NexusAdaptiveWorkerExplorerV3:

    def __init__(
        self,
        max_workers=4
    ):

        self.max_workers = max_workers
        self.memory = {}

    def key(
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
        workers,
        elapsed
    ):

        key = self.key(
            task_count,
            independent_tasks
        )

        self.ensure_pattern(key)

        if workers not in self.memory[key]:

            self.memory[key][workers] = WorkerStats()

        self.memory[key][workers].record(
            elapsed
        )

    def candidates(
        self,
        independent_tasks
    ):

        limit = min(
            self.max_workers,
            independent_tasks
        )

        if limit <= 1:

            return [1]

        return list(
            range(
                1,
                limit + 1
            )
        )

    def missing_workers(
        self,
        task_count,
        independent_tasks
    ):

        key = self.key(
            task_count,
            independent_tasks
        )

        self.ensure_pattern(key)

        known = self.memory[key]

        return [
            worker
            for worker in self.candidates(
                independent_tasks
            )
            if worker not in known
        ]

    def best_worker(
        self,
        task_count,
        independent_tasks
    ):

        key = self.key(
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
            key=lambda worker:
                stats[worker].average_time
        )

    def memory_size(self):

        return sum(
            len(stats)
            for stats in self.memory.values()
        )


class NexusAdaptiveWorkerExplorationEngineV3:

    def __init__(
        self,
        max_workers=4
    ):

        self.planner = (
            NexusAdaptiveWorkerExplorerV3(
                max_workers=max_workers
            )
        )

        self.tasks = {}
        self.results = {}

    def reset(self):

        self.results = {}

    def add_task(
        self,
        task_id,
        func,
        dependencies=None
    ):

        self.tasks[task_id] = {
            "func": func,
            "dependencies": (
                dependencies or []
            )
        }

    def ready_tasks(self):

        ready = []

        for task_id, task in self.tasks.items():

            if task_id in self.results:

                continue

            if all(
                dependency in self.results
                for dependency in task["dependencies"]
            ):

                ready.append(task_id)

        return ready

    def run_task(
        self,
        task_id
    ):

        task = self.tasks[task_id]

        arguments = [
            self.results[dependency]
            for dependency in task["dependencies"]
        ]

        return task["func"](*arguments)

    def execute_batch(
        self,
        ready,
        workers
    ):

        start = time.perf_counter()

        if workers == 1:

            values = {}

            for task_id in ready:

                values[task_id] = (
                    self.run_task(task_id)
                )

        else:

            worker_count = min(
                workers,
                len(ready)
            )

            values = {}

            with ThreadPoolExecutor(
                max_workers=worker_count
            ) as executor:

                futures = {
                    task_id:
                        executor.submit(
                            self.run_task,
                            task_id
                        )
                    for task_id in ready
                }

                for task_id, future in futures.items():

                    values[task_id] = (
                        future.result()
                    )

        elapsed = (
            time.perf_counter()
            - start
        )

        return values, elapsed

    def explore_workers(
        self,
        ready,
        task_count
    ):

        independent = len(ready)

        candidates = (
            self.planner.candidates(
                independent
            )
        )

        print()
        print(
            "EXPLORATION"
        )

        print(
            f"PATTERN: "
            f"({task_count}, {independent})"
        )

        print(
            f"CANDIDATES: {candidates}"
        )

        original_results = dict(
            self.results
        )

        measurements = []

        for workers in candidates:

            self.results = dict(
                original_results
            )

            values, elapsed = (
                self.execute_batch(
                    ready,
                    workers
                )
            )

            measurements.append({
                "workers": workers,
                "elapsed": elapsed,
                "values": values
            })

            print(
                f"  WORKERS={workers} "
                f"| TIME={elapsed:.6f}s"
            )

        self.results = dict(
            original_results
        )

        best = min(
            measurements,
            key=lambda item:
                item["elapsed"]
        )

        best_workers = best["workers"]
        best_time = best["elapsed"]

        print(
            f"BEST WORKERS: "
            f"{best_workers}"
        )

        print(
            f"BEST TIME: "
            f"{best_time:.6f}s"
        )

        for measurement in measurements:

            self.planner.record(
                task_count,
                independent,
                measurement["workers"],
                measurement["elapsed"]
            )

        return (
            best_workers,
            best_time
        )

    def execute(self):

        total_start = time.perf_counter()

        executions = 0
        batches = 0
        history = []

        while len(self.results) < len(
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
                self.planner.missing_workers(
                    task_count,
                    independent
                )
            )

            if missing:

                workers, _ = (
                    self.explore_workers(
                        ready,
                        task_count
                    )
                )

                values, elapsed = (
                    self.execute_batch(
                        ready,
                        workers
                    )
                )

                source = "EXPLORE"

            else:

                workers = (
                    self.planner.best_worker(
                        task_count,
                        independent
                    )
                )

                values, elapsed = (
                    self.execute_batch(
                        ready,
                        workers
                    )
                )

                source = "EXPLOIT"

            for task_id, value in values.items():

                self.results[task_id] = value

                executions += 1

            batches += 1

            history.append({
                "pattern": (
                    task_count,
                    independent
                ),
                "workers": workers,
                "source": source,
                "elapsed": elapsed
            })

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


def heavy_work(seed):

    total = 0

    for i in range(70000):

        total += (
            (i + seed)
            * (i + seed)
        )

    return total


def combine(
    a,
    b
):

    return a + b


def main():

    print(
        "=== NEXUS ADAPTIVE WORKER EXPLORATION V3 ==="
    )

    print()

    engine = (
        NexusAdaptiveWorkerExplorationEngineV3(
            max_workers=4
        )
    )

    # Four genuinely independent tasks.
    # This creates the target pattern:
    # (7, 4)
    engine.add_task(
        "A",
        lambda: heavy_work(1)
    )

    engine.add_task(
        "B",
        lambda: heavy_work(2)
    )

    engine.add_task(
        "C",
        lambda: heavy_work(3)
    )

    engine.add_task(
        "D",
        lambda: heavy_work(4)
    )

    # Second dependency layer.
    engine.add_task(
        "E",
        combine,
        ["A", "B"]
    )

    engine.add_task(
        "F",
        combine,
        ["C", "D"]
    )

    # Final dependency layer.
    engine.add_task(
        "G",
        combine,
        ["E", "F"]
    )

    total_runs = 4

    all_correct = True

    for run in range(
        1,
        total_runs + 1
    ):

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
                f"| WORKERS={item['workers']} "
                f"| SOURCE={item['source']} "
                f"| TIME={item['elapsed']:.6f}s"
            )

        results = result["results"]

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

        correct = (
            results["E"]
            == expected_e
            and
            results["F"]
            == expected_f
            and
            results["G"]
            == expected_g
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

    for key, stats in sorted(
        engine.planner.memory.items()
    ):

        print()

        print(
            f"PATTERN: {key}"
        )

        for workers, data in sorted(
            stats.items()
        ):

            print(
                f"  WORKERS={workers} "
                f"| RUNS={data.runs} "
                f"| AVG={data.average_time:.6f}s "
                f"| BEST={data.best_time:.6f}s"
            )

    print()
    print(
        f"MEMORY ENTRIES: "
        f"{engine.planner.memory_size()}"
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
