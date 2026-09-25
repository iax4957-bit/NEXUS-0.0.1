from nexus_router import NexusRouter
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend


class NexusRuntimeV3:
    def __init__(self, workers=4):
        self.router = NexusRouter()
        self.workers = workers

    def execute(self, tasks):
        groups = self.router.group_tasks(tasks)
        results = []

        for backend, backend_tasks in groups.items():

            if backend == "PROCESS":
                backend_results = NexusProcessBackend(
                    self.workers
                ).execute(backend_tasks)

            elif backend == "THREAD":
                backend_results = NexusThreadBackend(
                    self.workers
                ).execute(backend_tasks)

            else:
                backend_results = [
                    (task.task_id, task.run())
                    for task in backend_tasks
                ]

            results.extend(backend_results)

        return results
