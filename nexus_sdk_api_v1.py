from nexus_sdk_core_v1 import NexusUnifiedV2


class NEXUS:

    VERSION = "NEXUS SDK V1"

    def __init__(
        self,
        max_workers=None,
        exploration_repeats=2,
    ):
        self.engine = NexusUnifiedV2(
            max_workers=max_workers,
            exploration_repeats=exploration_repeats,
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

    def clear(self):
        self.engine.graph.tasks.clear()
        self.engine.results.clear()
        self.engine.cache.clear()
        self.engine.execution_count = 0
        self.engine.cache_hits = 0
        self.engine.batch_count = 0
