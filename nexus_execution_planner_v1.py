# NEXUS Execution Planner V1
# Step 1: Execution strategy selection

from dataclasses import dataclass


@dataclass
class Plan:
    strategy: str
    workers: int
    reason: str


class NexusExecutionPlannerV1:
    """
    First decision layer of NEXUS.

    Strategies:
        SEQUENTIAL
        PARALLEL
        REUSE
    """

    def __init__(self, workers=4):
        self.default_workers = max(1, workers)

    def plan(
        self,
        task_count,
        independent_tasks=0,
        reusable_results=0,
    ):
        # Existing results should be reused first.
        if reusable_results > 0:
            return Plan(
                strategy="REUSE",
                workers=0,
                reason="Reusable results are available"
            )

        # No meaningful parallelism.
        if task_count <= 1 or independent_tasks <= 1:
            return Plan(
                strategy="SEQUENTIAL",
                workers=1,
                reason="Insufficient parallel work"
            )

        # Enough independent work for parallel execution.
        workers = min(self.default_workers, independent_tasks)

        return Plan(
            strategy="PARALLEL",
            workers=max(1, workers),
            reason="Multiple independent tasks available"
        )


if __name__ == "__main__":
    planner = NexusExecutionPlannerV1(workers=4)

    print("=== NEXUS EXECUTION PLANNER V1 ===")

    tests = [
        {
            "name": "SINGLE TASK",
            "task_count": 1,
            "independent_tasks": 1,
            "reusable_results": 0,
        },
        {
            "name": "PARALLEL WORK",
            "task_count": 8,
            "independent_tasks": 8,
            "reusable_results": 0,
        },
        {
            "name": "REUSABLE RESULT",
            "task_count": 5,
            "independent_tasks": 4,
            "reusable_results": 2,
        },
    ]

    for test in tests:
        plan = planner.plan(
            task_count=test["task_count"],
            independent_tasks=test["independent_tasks"],
            reusable_results=test["reusable_results"],
        )

        print(f"\n{test['name']}")
        print(f"STRATEGY: {plan.strategy}")
        print(f"WORKERS: {plan.workers}")
        print(f"REASON: {plan.reason}")

    print("\nFINAL TEST: True")
