# NEXUS Execution Planner V2
# Adaptive performance-aware planning

from dataclasses import dataclass

from nexus_adaptive_plan_cache_v1 import (
    NexusAdaptivePlanCacheV1
)


@dataclass
class Plan:
    strategy: str
    workers: int
    reason: str
    source: str


class NexusExecutionPlannerV2:

    def __init__(self, workers=4):
        self.default_workers = max(1, workers)
        self.memory = NexusAdaptivePlanCacheV1()

    def _baseline_plan(
        self,
        task_count,
        independent_tasks
    ):
        if task_count <= 1 or independent_tasks <= 1:
            return Plan(
                strategy="SEQUENTIAL",
                workers=1,
                reason="Insufficient parallel work",
                source="BASELINE"
            )

        workers = min(
            self.default_workers,
            independent_tasks
        )

        return Plan(
            strategy="PARALLEL",
            workers=max(1, workers),
            reason="Multiple independent tasks available",
            source="BASELINE"
        )

    def plan(
        self,
        task_count,
        independent_tasks,
        reusable_results=0
    ):
        # Reuse always has priority.
        if reusable_results > 0:
            return Plan(
                strategy="REUSE",
                workers=0,
                reason="Reusable results are available",
                source="RULE"
            )

        baseline = self._baseline_plan(
            task_count,
            independent_tasks
        )

        stats = self.memory.get(
            task_count,
            independent_tasks
        )

        # No experience yet.
        if stats is None:
            return baseline

        # Do not trust very small samples.
        if stats.runs < 3:
            return Plan(
                strategy=baseline.strategy,
                workers=baseline.workers,
                reason=(
                    f"Insufficient history "
                    f"({stats.runs} runs)"
                ),
                source="BASELINE"
            )

        # Avoid unreliable learned decisions.
        if stats.reliability < 0.75:
            return Plan(
                strategy=baseline.strategy,
                workers=baseline.workers,
                reason=(
                    f"Learned reliability too low "
                    f"({stats.reliability:.2f})"
                ),
                source="BASELINE"
            )

        # Use learned strategy.
        return Plan(
            strategy=stats.strategy,
            workers=stats.workers,
            reason=(
                f"Learned from {stats.runs} runs, "
                f"avg={stats.average_time:.4f}s, "
                f"reliability={stats.reliability:.2f}"
            ),
            source="LEARNED"
        )

    def record_result(
        self,
        task_count,
        independent_tasks,
        strategy,
        workers,
        elapsed,
        success=True
    ):
        self.memory.record(
            task_count=task_count,
            independent_tasks=independent_tasks,
            strategy=strategy,
            workers=workers,
            elapsed=elapsed,
            success=success
        )


if __name__ == "__main__":

    print("=== NEXUS EXECUTION PLANNER V2 ===")

    planner = NexusExecutionPlannerV2(
        workers=4
    )

    # First decision: no history.
    first = planner.plan(
        task_count=8,
        independent_tasks=4
    )

    print("\nFIRST DECISION")
    print("STRATEGY:", first.strategy)
    print("WORKERS:", first.workers)
    print("SOURCE:", first.source)

    # Simulate three successful learned executions.
    for elapsed in (0.30, 0.28, 0.32):

        planner.record_result(
            task_count=8,
            independent_tasks=4,
            strategy="PARALLEL",
            workers=2,
            elapsed=elapsed,
            success=True
        )

    # Learned decision.
    learned = planner.plan(
        task_count=8,
        independent_tasks=4
    )

    print("\nLEARNED DECISION")
    print("STRATEGY:", learned.strategy)
    print("WORKERS:", learned.workers)
    print("SOURCE:", learned.source)
    print("REASON:", learned.reason)

    stats = planner.memory.get(
        task_count=8,
        independent_tasks=4
    )

    correct = (
        first.strategy == "PARALLEL"
        and first.source == "BASELINE"
        and learned.strategy == "PARALLEL"
        and learned.workers == 2
        and learned.source == "LEARNED"
        and stats is not None
        and stats.runs == 3
        and stats.successes == 3
        and stats.reliability == 1.0
    )

    print("\nFINAL TEST:", correct)
