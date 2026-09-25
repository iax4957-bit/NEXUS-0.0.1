from nexus_selector import NexusBackendSelector
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend


class NexusRuntimeV2:
    def __init__(self, workers=4):
        self.selector = NexusBackendSelector()
        self.workers = workers

    def execute(self, tasks):
        if not tasks:
            return []

        task_type = tasks[0].task_type
        backend = self.selector.select(task_type)

        if backend == "PROCESS":
            return NexusProcessBackend(self.workers).execute(tasks)

        if backend == "THREAD":
            return NexusThreadBackend(self.workers).execute(tasks)

        return [
            (task.task_id, task.run())
            for task in tasks
        ]
