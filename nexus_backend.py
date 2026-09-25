class NexusBackend:
    def execute(self, tasks):
        raise NotImplementedError


from concurrent.futures import ThreadPoolExecutor


class NexusThreadBackend(NexusBackend):
    def __init__(self, workers=4):
        self.workers = workers

    def execute(self, tasks):
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            return list(
                executor.map(
                    lambda task: (task.task_id, task.run()),
                    tasks
                )
            )
