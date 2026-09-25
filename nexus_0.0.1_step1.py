class NexusTask:
    def __init__(self, task_id, operation):
        self.task_id = task_id
        self.operation = operation
        self.result = None

    def run(self):
        self.result = self.operation()
        return self.result
class NexusGraph:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def task_count(self):
        return len(self.tasks)
def test_nexus():
    graph = NexusGraph()

    task1 = NexusTask(
        "TASK-1",
        lambda: 10 + 20
    )

    task2 = NexusTask(
        "TASK-2",
        lambda: 50 * 2
    )

    graph.add_task(task1)
    graph.add_task(task2)

    print("NEXUS 0.0.1")
    print("Tasks:", graph.task_count())

    for task in graph.tasks:
        print(task.task_id, "=>", task.run())


if __name__ == "__main__":
    test_nexus()
