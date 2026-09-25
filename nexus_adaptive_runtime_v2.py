import time

from nexus_performance_memory_v2 import NexusPerformanceMemoryV2
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend


class NexusAdaptiveRuntimeV2:
    def __init__(
        self,
        workers=4,
        memory_file="nexus_performance_v2.json"
    ):
        self.workers = workers
        self.memory = NexusPerformanceMemoryV2(memory_file)

    def choose_backend(
        self,
        task_type,
        workload_size
    ):
        backend = self.memory.best_backend(
            task_type,
            workload_size,
            self.workers
        )

        if backend is not None:
            return backend

        if task_type == "CPU":
            return "PROCESS"

        if task_type == "IO":
            return "THREAD"

        return "SEQUENTIAL"

    def execute(
        self,
        task_type,
        workload_size,
        tasks
    ):
        backend = self.choose_backend(
            task_type,
            workload_size
        )

        start = time.perf_counter()

        if backend == "PROCESS":
            results = NexusProcessBackend(
                self.workers
            ).execute(tasks)

        elif backend == "THREAD":
            results = NexusThreadBackend(
                self.workers
            ).execute(tasks)

        else:
            results = [
                (task.task_id, task.run())
                for task in tasks
            ]

        elapsed = time.perf_counter() - start

        self.memory.record(
            task_type,
            workload_size,
            self.workers,
            backend,
            elapsed
        )

        return backend, results, elapsed
