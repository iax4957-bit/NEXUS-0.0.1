from concurrent.futures import ProcessPoolExecutor


class NexusProcessBackend:
    def __init__(self, workers=4):
        self.workers = workers
    def execute(self, tasks):
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            return list(
                executor.map(
                    process_task,
                    tasks
                )
            )


def process_task(task):
    return (task.task_id, task.run())
