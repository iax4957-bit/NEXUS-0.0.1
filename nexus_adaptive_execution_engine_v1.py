# NEXUS Adaptive Execution Engine V1
# Execute -> Measure -> Learn

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from nexus_execution_planner_v2 import NexusExecutionPlannerV2


@dataclass
class NexusTask:
    name: str
    function: object
    dependencies: list


class NexusAdaptiveExecutionEngineV1:

    def __init__(self, workers=4):
        self.planner = NexusExecutionPlannerV2(
            workers=workers
        )

        self.tasks = {}
        self.results = {}

        self.execution_count = 0
        self.parallel_batches = 0

    def add_task(
        self,
        name,
        function,
        dependencies=None
    ):
        self.tasks[name] = NexusTask(
            name=name,
            function=function,
            dependencies=dependencies or []
        )

    def _ready_tasks(self):
        ready = []

        for name, task in self.tasks.items():

            if name in self.results:
                continue

            if all(
                dependency in self.results
                for dependency in task.dependencies
            ):
                ready.append(task)

        return ready

    def _run_task(self, task):

        args = [
            self.results[dependency]
            for dependency in task.dependencies
        ]

        return task.name, task.function(*args)

    def execute(self):

        total_start = time.perf_counter()

        while len(self.results) < len(self.tasks):

            ready = self._ready_tasks()

            if not ready:
                raise RuntimeError(
                    "Execution stopped: "
                    "dependency cycle or missing dependency"
                )

            independent_count = len(ready)

            plan = self.planner.plan(
                task_count=len(self.tasks),
                independent_tasks=independent_count
            )

            batch_start = time.perf_counter()

            success = True

            try:

                if plan.strategy == "SEQUENTIAL":

                    task = ready[0]

                    name, result = self._run_task(task)

                    self.results[name] = result
                    self.execution_count += 1

                elif plan.strategy == "PARALLEL":

                    workers = min(
                        plan.workers,
                        len(ready)
                    )

                    self.parallel_batches += 1

                    with ThreadPoolExecutor(
                        max_workers=workers
                    ) as executor:

                        completed = executor.map(
                            self._run_task,
                            ready
                        )

                        for name, result in completed:

                            self.results[name] = result
                            self.execution_count += 1

                elif plan.strategy == "REUSE":

                    raise RuntimeError(
                        "REUSE selected but no reusable "
                        "result was supplied"
                    )

            except Exception:

                success = False
                raise

            finally:

                batch_elapsed = (
                    time.perf_counter()
                    - batch_start
                )

                self.planner.record_result(
                    task_count=len(self.tasks),
                    independent_tasks=independent_count,
                    strategy=plan.strategy,
                    workers=plan.workers,
                    elapsed=batch_elapsed,
                    success=success
                )

        total_elapsed = (
            time.perf_counter()
            - total_start
        )

        return {
            "results": self.results,
            "elapsed": total_elapsed,
            "executions": self.execution_count,
            "parallel_batches": self.parallel_batches
        }


if __name__ == "__main__":

    print("=== NEXUS ADAPTIVE EXECUTION ENGINE V1 ===")

    engine = NexusAdaptiveExecutionEngineV1(
        workers=4
    )

    engine.add_task(
        "A",
        lambda: 10 * 10
    )

    engine.add_task(
        "B",
        lambda: 20 * 20
    )

    engine.add_task(
        "C",
        lambda: 30 * 30
    )

    engine.add_task(
        "D",
        lambda a, b: a + b,
        dependencies=["A", "B"]
    )

    engine.add_task(
        "E",
        lambda b, c: b + c,
        dependencies=["B", "C"]
    )

    engine.add_task(
        "F",
        lambda d, e: d + e,
        dependencies=["D", "E"]
    )

    # First execution
    first = engine.execute()

    print("\nFIRST EXECUTION")

    for name, result in first["results"].items():
        print(f"{name} RESULT: {result}")

    print("ELAPSED:", round(first["elapsed"], 6))
    print("EXECUTIONS:", first["executions"])
    print("PARALLEL BATCHES:", first["parallel_batches"])

    # Verify correctness
    correct = (
        first["results"]["A"] == 100
        and first["results"]["B"] == 400
        and first["results"]["C"] == 900
        and first["results"]["D"] == 500
        and first["results"]["E"] == 1300
        and first["results"]["F"] == 1800
    )

    print("\nRESULTS CORRECT:", correct)

    # Inspect learned memory
    learned_entries = len(
        engine.planner.memory.cache
    )

    print(
        "LEARNED MEMORY ENTRIES:",
        learned_entries
    )

    print(
        "\nFINAL TEST:",
        correct and learned_entries > 0
    )
