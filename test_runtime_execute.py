from nexus_runtime import NexusRuntime


def cpu_work(n):
    total = 0

    for i in range(1, n):
        total += (i * i) % 1000003

    return total


class Task:
    def __init__(self, task_id, n):
        self.task_id = task_id
        self.n = n

    def run(self):
        return cpu_work(self.n)


def main():
    tasks = [
        Task("R1", 1_000_000),
        Task("R2", 1_000_000),
        Task("R3", 1_000_000),
        Task("R4", 1_000_000),
    ]

    runtime = NexusRuntime(workers=4)

    results = runtime.execute("CPU", tasks)

    print("NEXUS RUNTIME EXECUTION TEST")
    print("Selected backend:", runtime.choose_backend("CPU"))

    for task_id, result in results:
        print(task_id, "=>", result)


if __name__ == "__main__":
    main()
