import time

from nexus_adaptive_learning_v4 import NexusAdaptiveLearningV4
from nexus_performance_memory_v3 import NexusPerformanceMemoryV3
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend


class NexusAdaptiveRuntimeV4:
    def __init__(
        self,
        workers=4,
        memory_file="nexus_performance_v3.json"
    ):
        self.workers = workers
        self.memory = NexusPerformanceMemoryV3(memory_file)
        self.learning = NexusAdaptiveLearningV4()

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
            "confidence": decision["confidence"],
            "elapsed": elapsed,
            "results": results
        }
