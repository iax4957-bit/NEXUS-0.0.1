# NEXUS Plan Cache V1
# Decision memory for the Execution Planner

from dataclasses import dataclass


@dataclass
class CachedPlan:
    strategy: str
    workers: int
    hits: int = 0


class NexusPlanCacheV1:

    def __init__(self):
        self.cache = {}

    def _make_key(self, task_count, independent_tasks):
        return (
            int(task_count),
            int(independent_tasks)
        )

    def get(self, task_count, independent_tasks):
        key = self._make_key(
            task_count,
            independent_tasks
        )

        plan = self.cache.get(key)

        if plan is None:
            return None

        plan.hits += 1
        return plan

    def store(
        self,
        task_count,
        independent_tasks,
        strategy,
        workers
    ):
        key = self._make_key(
            task_count,
            independent_tasks
        )

        self.cache[key] = CachedPlan(
            strategy=strategy,
            workers=workers
        )

    def size(self):
        return len(self.cache)

    def clear(self):
        self.cache.clear()


if __name__ == "__main__":

    print("=== NEXUS PLAN CACHE V1 ===")

    cache = NexusPlanCacheV1()

    # First decision: store it.
    cache.store(
        task_count=6,
        independent_tasks=3,
        strategy="PARALLEL",
        workers=3
    )

    print("CACHE SIZE:", cache.size())

    # Second request: retrieve it.
    plan = cache.get(
        task_count=6,
        independent_tasks=3
    )

    print("CACHE HIT:", plan is not None)

    if plan:
        print("STRATEGY:", plan.strategy)
        print("WORKERS:", plan.workers)
        print("HITS:", plan.hits)

    # Unknown pattern.
    missing = cache.get(
        task_count=10,
        independent_tasks=1
    )

    print("UNKNOWN PATTERN:", missing is None)

    correct = (
        cache.size() == 1
        and plan is not None
        and plan.strategy == "PARALLEL"
        and plan.workers == 3
        and plan.hits == 1
        and missing is None
    )

    print("\nFINAL TEST:", correct)
