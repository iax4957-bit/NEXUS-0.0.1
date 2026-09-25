# NEXUS Adaptive Plan Cache V1
# Performance-aware decision memory

from dataclasses import dataclass


@dataclass
class PlanStats:
    strategy: str
    workers: int
    runs: int = 0
    successes: int = 0
    failures: int = 0
    total_time: float = 0.0

    @property
    def average_time(self):
        if self.runs == 0:
            return 0.0

        return self.total_time / self.runs

    @property
    def reliability(self):
        if self.runs == 0:
            return 0.0

        return self.successes / self.runs


class NexusAdaptivePlanCacheV1:

    def __init__(self):
        self.cache = {}

    def _make_key(self, task_count, independent_tasks):
        return (
            int(task_count),
            int(independent_tasks)
        )

    def record(
        self,
        task_count,
        independent_tasks,
        strategy,
        workers,
        elapsed,
        success=True
    ):
        key = self._make_key(
            task_count,
            independent_tasks
        )

        stats = self.cache.get(key)

        if stats is None:
            stats = PlanStats(
                strategy=strategy,
                workers=workers
            )

            self.cache[key] = stats

        stats.runs += 1
        stats.total_time += float(elapsed)

        if success:
            stats.successes += 1
        else:
            stats.failures += 1

    def get(self, task_count, independent_tasks):
        key = self._make_key(
            task_count,
            independent_tasks
        )

        return self.cache.get(key)

    def size(self):
        return len(self.cache)

    def clear(self):
        self.cache.clear()


if __name__ == "__main__":

    print("=== NEXUS ADAPTIVE PLAN CACHE V1 ===")

    cache = NexusAdaptivePlanCacheV1()

    # Simulate three successful runs.
    cache.record(
        task_count=6,
        independent_tasks=3,
        strategy="PARALLEL",
        workers=3,
        elapsed=0.30,
        success=True
    )

    cache.record(
        task_count=6,
        independent_tasks=3,
        strategy="PARALLEL",
        workers=3,
        elapsed=0.40,
        success=True
    )

    cache.record(
        task_count=6,
        independent_tasks=3,
        strategy="PARALLEL",
        workers=3,
        elapsed=0.50,
        success=True
    )

    # Simulate one failure.
    cache.record(
        task_count=6,
        independent_tasks=3,
        strategy="PARALLEL",
        workers=3,
        elapsed=0.60,
        success=False
    )

    stats = cache.get(
        task_count=6,
        independent_tasks=3
    )

    print("CACHE SIZE:", cache.size())

    if stats:

        print("STRATEGY:", stats.strategy)
        print("WORKERS:", stats.workers)
        print("RUNS:", stats.runs)
        print("SUCCESSES:", stats.successes)
        print("FAILURES:", stats.failures)
        print("TOTAL TIME:", round(stats.total_time, 3))
        print("AVERAGE TIME:", round(stats.average_time, 3))
        print("RELIABILITY:", round(stats.reliability, 3))

    correct = (
        cache.size() == 1
        and stats is not None
        and stats.runs == 4
        and stats.successes == 3
        and stats.failures == 1
        and abs(stats.total_time - 1.8) < 0.000001
        and abs(stats.average_time - 0.45) < 0.000001
        and abs(stats.reliability - 0.75) < 0.000001
    )

    print("\nFINAL TEST:", correct)
