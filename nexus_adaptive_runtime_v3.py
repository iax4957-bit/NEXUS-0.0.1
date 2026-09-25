import time

from nexus_adaptive_learning_v3 import NexusAdaptiveLearningV3
from nexus_performance_memory_v2 import NexusPerformanceMemoryV2
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend


class NexusAdaptiveRuntimeV3:
    def __init__(
        self,
        workers=4,
        memory_file="nexus_performance_v2.json"
    ):
        self.workers = workers

        self.memory = NexusPerformanceMemoryV2(
            memory_file
        )

        self.learning = NexusAdaptiveLearningV3()

    def execute(
        self,
        task_type,
        workload_size,
        tasks
    ):
        history = self.memory.get_history(
            task_type,
            workload_size,
            self.workers
        )

        decision = self.learning.decide(
            history,
            task_type
        )

        backend = decision["backend"]

        start = time.perf_counter()

        if backend == "PROCESS":
            results = NexusProcessBackend(
                self.workers
            ).execute(tasks)

        elif backend == "THREAD":
            results = NexusThreadBackend(
                self.workers
            ).execute(tasks)

        elif backend == "SEQUENTIAL":
            results = [
                (task.task_id, task.run())
                for task in tasks
            ]

        else:
            raise ValueError(
                f"Unknown backend: {backend}"
            )

        elapsed = time.perf_counter() - start

        self.memory.record(
            task_type,
            workload_size,
            self.workers,
            backend,
            elapsed
        )

        return {
            "mode": decision["mode"],
            "backend": backend,
            "elapsed": elapsed,
            "results": results
        }
