from nexus_process_backend import NexusProcessBackend


def work(value):
    return value * value


class TestTask:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return work(self.value)


def main():
    tasks = [
        TestTask("P1", 10),
        TestTask("P2", 20),
        TestTask("P3", 30),
        TestTask("P4", 40),
    ]

    backend = NexusProcessBackend(workers=4)
    results = backend.execute(tasks)

    print("NEXUS PROCESS BACKEND TEST")

    for task_id, result in results:
        print(task_id, "=>", result)


if __name__ == "__main__":
    main()
