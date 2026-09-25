import time
from concurrent.futures import ThreadPoolExecutor


class WorkerStats:

    def __init__(self):
        self.runs = 0
        self.total_time = 0.0

    @property
    def average_time(self):
        if self.runs == 0:
            return float("inf")
        return self.total_time / self.runs

    def record(self, elapsed):
        self.runs += 1
        self.total_time += elapsed


class NexusAdaptiveWorkerExplorationV1:

    def __init__(self, max_workers=4):

        self.max_workers = max_workers
        self.memory = {}

    def _key(self, task_count, independent_tasks):
        return (
            task_count,
            independent_tasks
        )

    def _ensure_memory(self, key):

        if key not in self.memory:
            self.memory[key] = {}

    def record(
        self,
        task_count,
        independent_tasks,
        workers,
        elapsed
    ):

        key = self._key(
            task_count,
            independent_tasks
        )

        self._ensure_memory(key)

        if workers not in self.memory[key]:
            self.memory[key][workers] = WorkerStats()

        self.memory[key][workers].record(
            elapsed
        )

    def candidates(self, independent_tasks):

        if independent_tasks <= 1:
            return [1]

        return list(
            range(
                1,
                min(
                    self.max_workers,
                    independent_tasks
                ) + 1
            )
        )

    def best_worker(
        self,
        task_count,
        independent_tasks
    ):

        key = self._key(
            task_count,
            independent_tasks
        )

        stats = self.memory.get(key, {})

        if not stats:
            return None

        return min(
            stats,
            key=lambda workers:
                stats[workers].average_time
        )

    def memory_size(self):

        return sum(
            len(stats)
            for stats in self.memory.values()
        )


class NexusAdaptiveWorkerExplorationEngineV1:

    def __init__(self, max_workers=4):

        self.planner = (
            NexusAdaptiveWorkerExplorationV1(
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
            "dependencies": dependencies or []
        }

    def _ready_tasks(self):

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

    def _run_task(self, task_id):

        task = self.tasks[task_id]

        args = [
            self.results[dep]
            for dep in task["dependencies"]
        ]

        return task["func"](*args)

    def _execute_batch(
        self,
        ready,
        workers
    ):

        batch_start = time.perf_counter()

        if workers == 1:

            values = {}

            for task_id in ready:
                values[task_id] = (
                    self._run_task(task_id)
                )

        else:

            values = {}

            workers = min(
                workers,
                len(ready)
            )

            with ThreadPoolExecutor(
                max_workers=workers
            ) as executor:

                futures = {
                    executor.submit(
                        self._run_task,
                        task_id
                    ): task_id
                    for task_id in ready
                }

                for future, task_id in futures.items():
                    values[task_id] = future.result()

        elapsed = (
            time.perf_counter()
            - batch_start
        )

        return values, elapsed

    def execute(self):

        total_start = time.perf_counter()

        executions = 0
        batches = 0
        history = []

        while len(self.results) < len(self.tasks):

            ready = self._ready_tasks()

            if not ready:
                raise RuntimeError(
                    "No executable tasks available."
                )

            independent = len(ready)

            candidates = self.planner.candidates(
                independent
            )

            key = (
                len(self.tasks),
                independent
            )

            known = self.planner.memory.get(
                key,
                {}
            )

            missing = [
                worker
                for worker in candidates
                if worker not in known
            ]

            if missing:

                workers = missing[0]
                source = "EXPLORE"

            else:

                workers = self.planner.best_worker(
                    len(self.tasks),
                    independent
                )

                source = "EXPLOIT"

            values, elapsed = self._execute_batch(
                ready,
                workers
            )

            for task_id, value in values.items():
                self.results[task_id] = value
                executions += 1

            batches += 1

            self.planner.record(
                len(self.tasks),
                independent,
                workers,
                elapsed
            )

            history.append({
                "pattern": (
                    len(self.tasks),
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
            "results": dict(self.results),
            "elapsed": total_elapsed,
            "executions": executions,
            "batches": batches,
            "history": history
        }


def main():

    print(
        "=== NEXUS ADAPTIVE WORKER EXPLORATION V1 ==="
    )
    print()

    engine = (
        NexusAdaptiveWorkerExplorationEngineV1(
            max_workers=4
        )
    )

    def heavy():

        return sum(
            i * i
            for i in range(30000)
        )

    def add(a, b):
        return a + b

    engine.add_task("A", heavy)
    engine.add_task("B", heavy)
    engine.add_task("C", heavy)

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

    for run in range(1, 7):

        engine.reset()

        result = engine.execute()

        print("=" * 75)
        print(f"RUN {run}")
        print("=" * 75)

        print(
            f"TIME: {result['elapsed']:.6f}s"
        )

        for item in result["history"]:

            print(
                f"PATTERN: {item['pattern']} | "
                f"workers={item['workers']} | "
                f"source={item['source']} | "
                f"time={item['elapsed']:.6f}s"
            )

        correct = (
            result["results"]["D"]
            == (
                result["results"]["A"]
                + result["results"]["B"]
            )
            and
            result["results"]["E"]
            == (
                result["results"]["B"]
                + result["results"]["C"]
            )
            and
            result["results"]["F"]
            == (
                result["results"]["D"]
                + result["results"]["E"]
            )
        )

        print()
        print(f"CORRECT: {correct}")
        print()

    print("=" * 75)
    print("EXPLORATION SUMMARY")
    print("=" * 75)

    for key, stats in engine.planner.memory.items():

        print(
            f"PATTERN: {key}"
        )

        for workers, data in sorted(
            stats.items()
        ):

            print(
                f"  WORKERS={workers} | "
                f"RUNS={data.runs} | "
                f"AVG={data.average_time:.6f}s"
            )

    print()
    print(
        f"MEMORY ENTRIES: "
        f"{engine.planner.memory_size
