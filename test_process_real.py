from nexus_process_backend import NexusProcessBackend


def cpu_work(n):
    total = 0

    for i in range(1, n):
        total += (i * i) % 1000003

    return total


class TestTask:
    def __init__(self, task_id, n):
        self.task_id = task_id
        self.n = n

    def run(self):
        return cpu_work(self.n)


def main():
    tasks = [
        TestTask("CPU-1", 1_000_000),
        TestTask("CPU-2", 1_000_000),
        TestTask("CPU-3", 1_000_000),
        TestTask("CPU-4", 1_000_000),
    ]

    backend = NexusProcessBackend(workers=4)

    results = backend.execute(tasks)

    print("NEXUS PROCESS CPU TEST")

    for task_id, result in results:
        print(task_id, "=>", result)


if __name__ == "__main__":
    main()
