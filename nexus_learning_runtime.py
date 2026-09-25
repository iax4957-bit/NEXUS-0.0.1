from nexus_performance_memory import NexusPerformanceMemory
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend


class NexusLearningRuntime:
    def __init__(self, workers=4, memory_file="nexus_performance.json"):
        self.workers = workers
        self.memory = NexusPerformanceMemory(memory_file)

    def choose_backend(self, task_type):
        backend = self.memory.best_backend(task_type)

        if backend is not None:
            return backend

        if task_type == "CPU":
            return "PROCESS"

        if task_type == "IO":
            return "THREAD"

        return "SEQUENTIAL"

    def execute(self, task_type, tasks):
        backend = self.choose_backend(task_type)

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

        return backend, results
