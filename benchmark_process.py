import time

from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend


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


def sequential(tasks):
    return [(task.task_id, task.run()) for task in tasks]


def main():
    n = 1_000_000

    tasks = [
        Task("CPU-1", n),
        Task("CPU-2", n),
        Task("CPU-3", n),
        Task("CPU-4", n),
    ]

    start = time.perf_counter()
    sequential_results = sequential(tasks)
    sequential_time = time.perf_counter() - start

    tasks = [
        Task("CPU-1", n),
        Task("CPU-2", n),
        Task("CPU-3", n),
        Task("CPU-4", n),
    ]

    start = time.perf_counter()
    thread_results = NexusThreadBackend(workers=4).execute(tasks)
    thread_time = time.perf_counter() - start

    tasks = [
        Task("CPU-1", n),
        Task("CPU-2", n),
        Task("CPU-3", n),
        Task("CPU-4", n),
    ]

    start = time.perf_counter()
    process_results = NexusProcessBackend(workers=4).execute(tasks)
    process_time = time.perf_counter() - start

    print()
    print("================================")
    print("NEXUS REAL CPU BENCHMARK")
    print("================================")

    print(f"Sequential: {sequential_time:.3f} seconds")
    print(f"Threads:    {thread_time:.3f} seconds")
    print(f"Processes:  {process_time:.3f} seconds")

    print()

    print(f"Thread speedup:   {sequential_time / thread_time:.2f}x")
    print(f"Process speedup:  {sequential_time / process_time:.2f}x")

    print()

    print("Thread results match:",
          thread_results == sequential_results)

    print("Process results match:",
          process_results == sequential_results)


if __name__ == "__main__":
    main()
