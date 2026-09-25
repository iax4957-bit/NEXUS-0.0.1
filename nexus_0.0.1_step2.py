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
class NexusScheduler:
    def __init__(self):
        self.queue = []

    def submit(self, task):
        self.queue.append(task)

    def pending_tasks(self):
        return len(self.queue)

    def next_task(self):
        if not self.queue:
            return None

        return self.queue.pop(0)
def scheduler_test():
    graph = NexusGraph()
    scheduler = NexusScheduler()

    task1 = NexusTask("TASK-A", lambda: 100 + 50)
    task2 = NexusTask("TASK-B", lambda: 20 * 5)
    task3 = NexusTask("TASK-C", lambda: 7 * 7)

    graph.add_task(task1)
    graph.add_task(task2)
    graph.add_task(task3)

    for task in graph.tasks:
        scheduler.submit(task)

    print()
    print("NEXUS SCHEDULER TEST")
    print("Pending:", scheduler.pending_tasks())

    while scheduler.pending_tasks() > 0:
        task = scheduler.next_task()
        print(task.task_id, "=>", task.run())

    print("Pending:", scheduler.pending_tasks())
print()
scheduler_test()
class NexusExecutor:
    def execute(self, scheduler):
        results = []

        while scheduler.pending_tasks() > 0:
            task = scheduler.next_task()

            if task is not None:
                result = task.run()
                results.append((task.task_id, result))

        return results
def executor_test():
    scheduler = NexusScheduler()

    scheduler.submit(
        NexusTask("EXEC-1", lambda: 12 * 12)
    )

    scheduler.submit(
        NexusTask("EXEC-2", lambda: 100 + 25)
    )

    scheduler.submit(
        NexusTask("EXEC-3", lambda: 9 * 9)
    )

    executor = NexusExecutor()

    results = executor.execute(scheduler)

    print()
    print("NEXUS EXECUTOR TEST")

    for task_id, result in results:
        print(task_id, "=>", result)
executor_test()
