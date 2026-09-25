"""
NEXUS Runtime V1
Application-facing runtime layer for NEXUS 0.0.1
"""

from nexus_unified_v2 import NexusUnifiedV2


class NexusRuntimeV1:
    """
    Stable application-facing interface.

    Applications should communicate with this class
    instead of directly depending on the internal engine.
    """

    VERSION = "NEXUS RUNTIME V1"

    def __init__(self, max_workers=4):
        self.engine = NexusUnifiedV2(
            max_workers=max_workers,
            exploration_repeats=2,
        )

    def add_task(
        self,
        task_id,
        operation,
        args=(),
        dependencies=(),
    ):
        self.engine.add_task(
            task_id,
            operation,
            args,
            dependencies,
        )

    def run(self):
        return self.engine.run()

    def get_results(self):
        return dict(self.engine.results)

    def stats(self):
        return {
            "version": self.VERSION,
            "executions": self.engine.execution_count,
            "cache_hits": self.engine.cache_hits,
            "batches": self.engine.batch_count,
            "cache_size": len(self.engine.cache),
            "results": len(self.engine.results),
        }
