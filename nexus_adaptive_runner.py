import time

from nexus_adaptive import NexusAdaptiveEngine
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend


class NexusAdaptiveRunner:
    def __init__(self, workers=4):
        self.workers = workers
        self.adaptive = NexusAdaptiveEngine()

    def run_backend(self, task_type, backend, tasks):
        if backend == "PROCESS":
            executor = NexusProcessBackend(self.workers)

        elif backend == "THREAD":
            executor = NexusThreadBackend(self.workers)

        elif backend == "SEQUENTIAL":
            start = time.perf_counter()

            results = [
                (task.task_id, task.run())
                for task in tasks
            ]

            elapsed = time.perf_counter() - start

            self.adaptive.record(
                task_type,
                backend,
                elapsed
            )

            return results, elapsed

        else:
            raise ValueError(f"Unknown backend: {backend}")

        start = time.perf_counter()

        results = executor.execute(tasks)

        elapsed = time.perf_counter() - start

        self.adaptive.record(
            task_type,
            backend,
            elapsed
        )

        return results, elapsed
