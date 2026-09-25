# NEXUS Execution Engine V2
# Planner-driven execution

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from nexus_execution_planner_v1 import NexusExecutionPlannerV1


@dataclass
class NexusTask:
    name: str
    function: object
    dependencies: list


class NexusExecutionEngineV2:

    def __init__(self, workers=4):
        self.planner = NexusExecutionPlannerV1(workers=workers)
        self.tasks = {}
        self.results = {}
        self.execution_count = 0
        self.parallel_batches = 0

    def add_task(self, name, function, dependencies=None):
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

            if all(dep in self.results for dep in task.dependencies):
                ready.append(task)

        return ready

    def _run_task(self, task):
        args = [
            self.results[dependency]
            for dependency in task.dependencies
        ]

        return task.name, task.function(*args)

    def execute(self):
        while len(self.results) < len(self.tasks):

            ready = self._ready_tasks()

            if not ready:
                raise RuntimeError(
                    "Execution stopped: dependency cycle or missing dependency"
                )

            independent_count = len(ready)

            plan = self.planner.plan(
                task_count=len(self.tasks),
                independent_tasks=independent_count,
                reusable_results=0
            )

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
                pass

        return self.results


if __name__ == "__main__":

    print("=== NEXUS EXECUTION ENGINE V2 ===")

    engine = NexusExecutionEngineV2(workers=4)

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

    results = engine.execute()

    print(f"A RESULT: {results['A']}")
    print(f"B RESULT: {results['B']}")
    print(f"C RESULT: {results['C']}")
    print(f"D RESULT: {results['D']}")
    print(f"E RESULT: {results['E']}")
    print(f"F RESULT: {results['F']}")

    print(f"\nTASKS: {len(engine.tasks)}")
    print(f"REAL EXECUTIONS: {engine.execution_count}")
    print(f"PARALLEL BATCHES: {engine.parallel_batches}")

    correct = (
        results["A"] == 100
        and results["B"] == 400
        and results["C"] == 900
        and results["D"] == 500
        and results["E"] == 1300
        and results["F"] == 1800
    )

    print(f"\nRESULTS CORRECT: {correct}")
    print(f"ALL TASKS COMPLETED: {len(results) == len(engine.tasks)}")

    print("\nFINAL TEST:", correct and len(results) == len(engine.tasks))
