nano nexus_adaptive_execution_engine_v2.pyimport time
from concurrent.futures import ThreadPoolExecutor

from nexus_execution_planner_v2 import NexusExecutionPlannerV2


class NexusTask:
    def __init__(self, task_id, func, dependencies=None):
        self.task_id = task_id
        self.func = func
        self.dependencies = dependencies or []


class NexusAdaptiveExecutionEngineV2:

    def __init__(self, default_workers=4):
        self.planner = NexusExecutionPlannerV2(
            workers=default_workers
        )

        self.tasks = {}
        self.results = {}

        self.reset_run()
    def reset_run(self):
        """
        Reset only per-run execution state.

        Learned planner memory is preserved.
        """
        self.results = {}
        self.executions = 0
        self.parallel_batches = 0
        self.run_history = []

    def add_task(self, task):
        self.tasks[task.task_id] = task

    def _ready_tasks(self):
        ready = []

        for task_id, task in self.tasks.items():
            if task_id in self.results:
                continue

            if all(dep in self.results for dep in task.dependencies):
                ready.append(task)

        return ready

    def _execute_task(self, task):
        args = [
            self.results[dep]
            for dep in task.dependencies
        ]

        return task.func(*args)

    def execute(self):
        start_total = time.perf_counter()

        while len(self.results) < len(self.tasks):

            ready = self._ready_tasks()

            if not ready:
                raise RuntimeError(
                    "No executable tasks available. "
                    "Possible circular dependency."
                )

            independent_tasks = len(ready)

            plan = self.planner.plan(
                task_count=len(self.tasks),
                independent_tasks=independent_tasks,
                reusable_results=0
            )

            batch_start = time.perf_counter()

            if plan.strategy == "SEQUENTIAL":

                for task in ready:
                    self.results[task.task_id] = \
                        self._execute_task(task)

                    self.executions += 1

            elif plan.strategy == "PARALLEL":

                self.parallel_batches += 1

                workers = min(
                    plan.workers,
                    len(ready)
                )

                with ThreadPoolExecutor(
                    max_workers=workers
                ) as executor:

                    futures = {
                        executor.submit(
                            self._execute_task,
                            task
                        ): task
                        for task in ready
                    }

                    for future, task in [
                        (future, futures[future])
                        for future in futures
                    ]:
                        self.results[task.task_id] = \
                            future.result()

                        self.executions += 1

            else:
                raise RuntimeError(
                    f"Unsupported strategy: {plan.strategy}"
                )

            batch_elapsed = (
                time.perf_counter() - batch_start
            )

            self.planner.record_result(
                task_count=len(self.tasks),
                independent_tasks=independent_tasks,
                strategy=plan.strategy,
                workers=plan.workers,
                elapsed=batch_elapsed,
                success=True
            )

            self.run_history.append({
                "pattern": (
                    len(self.tasks),
                    independent_tasks
                ),
                "strategy": plan.strategy,
                "workers": plan.workers,
                "source": plan.source,
                "elapsed": batch_elapsed
            })

        total_elapsed = (
            time.perf_counter() - start_total
        )

        return {
            "results": dict(self.results),
            "elapsed": total_elapsed,
            "executions": self.executions,
            "parallel_batches": self.parallel_batches,
            "history": list(self.run_history)
        }
