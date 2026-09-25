from nexus_selector import NexusBackendSelector
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend


class NexusRuntime:
    def __init__(self, workers=4):
        self.selector = NexusBackendSelector()
        self.workers = workers

    def choose_backend(self, task_type):
        return self.selector.select(task_type)

    def execute(self, task_type, tasks):
        backend = self.choose_backend(task_type)

        if backend == "PROCESS":
            return NexusProcessBackend(self.workers).execute(tasks)

        if backend == "THREAD":
            return NexusThreadBackend(self.workers).execute(tasks)

        return [
            (task.task_id, task.run())
            for task in tasks
        ]
