from nexus_selector import NexusBackendSelector


class NexusRouter:
    def __init__(self):
        self.selector = NexusBackendSelector()

    def group_tasks(self, tasks):
        groups = {}

        for task in tasks:
            backend = self.selector.select(task.task_type)

            if backend not in groups:
                groups[backend] = []

            groups[backend].append(task)

        return groups
