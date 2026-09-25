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


class NexusAdaptiveWorkerExplorerV2:

    def __init__(
        self,
        max_workers=4,
        exploration_runs=1
    ):

        self.max_workers = max_workers
        self.exploration_runs = exploration_runs
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


class NexusAdaptiveWorkerExplorationEngineV2:

    def __init__(
        self,
        max_workers=4
    ):

        self.planner = (
            NexusAdaptiveWorkerExplorerV2(
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
                dep in self.results
                for dep in task["dependencies"]
            ):

                ready.append(task_id)

        return ready

    def run_task(
        self,
        task_id
    ):

        task = self.tasks[task_id]

        args = [
            self.results[dep]
            for dep in task["dependencies"]
        ]

        return task["func"](*args)

    def execute_batch(
        self,
        ready,
        workers
    ):

        start = time.perf_counter()

        if workers <= 1:

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

        measurements = []

        original_results = dict(
            self.results
        )

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

            measurements.append(
                (
                    workers,
                    elapsed,
                    values
                )
            )

            print(
                f"  WORKERS={workers} "
                f"| TIME={elapsed:.6f}s"
            )

        self.results = dict(
            original_results
        )

        best_workers, best_time, best_values = min(
            measurements,
            key=lambda item: item[1]
        )

        print(
            f"BEST WORKERS: {best_workers}"
        )

        print(
            f"BEST TIME: {best_time:.6f}s"
        )

        for workers, elapsed, _ in measurements:

            self.planner.record(
                task_count,
                independent,
                workers,
                elapsed
            )

        return (
            best_workers,
            best_values,
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

                workers, values, elapsed = (
                    self.explore_workers(
                        ready,
                        task_count
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


def heavy_work():

    total = 0

    for i in range(60000):

        total += (
            i * i
        )

    return total


def add(
    a,
    b
):

    return a + b


def main():

    print(
        "=== NEXUS ADAPTIVE WORKER EXPLORATION V2 ==="
    )

    print()

    engine = (
        NexusAdaptiveWorkerExplorationEngineV2(
            max_workers=4
        )
    )

    engine.add_task(
        "A",
        heavy_work
    )

    engine.add_task(
        "B",
        heavy_work
    )

    engine.add_task(
        "C",
        heavy_work
    )

    engine.add_task(
        "D",
        add,
        ["A", "B"]
    )

    engine.add_task(
        "E",
        add,
        ["B", "C"]
    )

    engine.add_task(
        "F",
        add,
        ["D", "E"]
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

        correct = (
            results["D"]
            == (
                results["A"]
                + results["B"]
            )
            and
            results["E"]
            == (
                results["B"]
                + results["C"]
            )
            and
            results["F"]
            == (
                results["D"]
                + results["E"]
            )
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
        "FINAL TEST: "
        f"{all_correct}"
    )


if __name__ == "__main__":

    main()
