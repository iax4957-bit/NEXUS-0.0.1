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


class NexusAdaptiveWorkerPlannerV1:

    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.memory = {}

    def _key(self, task_count, independent_tasks):
        return (
            task_count,
            independent_tasks
        )

    def choose_workers(
        self,
        task_count,
        independent_tasks
    ):

        if independent_tasks <= 1:
            return 1, "SEQUENTIAL"

        key = self._key(
            task_count,
            independent_tasks
        )

        stats = self.memory.get(key)

        if stats:

            best_worker = min(
                stats,
                key=lambda w: stats[w].average_time
            )

            return (
                best_worker,
                "LEARNED"
            )

        workers = min(
            self.max_workers,
            independent_tasks
        )

        return workers, "BASELINE"

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

        if key not in self.memory:
            self.memory[key] = {}

        if workers not in self.memory[key]:
            self.memory[key][workers] = WorkerStats()

        self.memory[key][workers].record(
            elapsed
        )

    def memory_size(self):
        return sum(
            len(workers)
            for workers in self.memory.values()
        )


class NexusWorkerEngineV1:

    def __init__(self, max_workers=4):

        self.max_workers = max_workers
        self.planner = NexusAdaptiveWorkerPlannerV1(
            max_workers=max_workers
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

    def execute(self):

        start_total = time.perf_counter()

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

            workers, source = (
                self.planner.choose_workers(
                    len(self.tasks),
                    independent
                )
            )

            batch_start = time.perf_counter()

            if workers == 1:

                for task_id in ready:

                    self.results[task_id] = (
                        self._run_task(task_id)
                    )

                    executions += 1

            else:

                batches += 1

                workers = min(
                    workers,
                    len(ready)
                )

                with ThreadPoolExecutor(
                    max_workers=
