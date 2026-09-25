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
from concurrent.futures import ThreadPoolExecutor


class NexusParallelExecutor:
    def __init__(self, workers=4):
        self.workers = workers

    def execute(self, scheduler):
        tasks = []

        while scheduler.pending_tasks() > 0:
            task = scheduler.next_task()

            if task is not None:
                tasks.append(task)

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            results = list(
                executor.map(
                    lambda task: (task.task_id, task.run()),
                    tasks
                )
            )

        return results
def parallel_test():
    import time

    def work(seconds):
        time.sleep(seconds)
        return seconds

    scheduler = NexusScheduler()

    for i in range(4):
        scheduler.submit(
            NexusTask(
                f"PAR-{i + 1}",
                lambda s=1: work(s)
            )
        )

    executor = NexusParallelExecutor(workers=4)

    start = time.perf_counter()

    results = executor.execute(scheduler)

    elapsed = time.perf_counter() - start

    print()
    print("NEXUS PARALLEL TEST")

    for task_id, result in results:
        print(task_id, "=>", result)

    print(f"Time: {elapsed:.3f} seconds")


parallel_test()
class NexusDependencyGraph:
    def __init__(self):
        self.tasks = {}
        self.dependencies = {}

    def add_task(self, task):
        self.tasks[task.task_id] = task
        self.dependencies[task.task_id] = []

    def add_dependency(self, task_id, depends_on):
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task: {task_id}")

        if depends_on not in self.tasks:
            raise ValueError(f"Unknown dependency: {depends_on}")

        self.dependencies[task_id].append(depends_on)

    def ready_tasks(self, completed):
        ready = []

        for task_id, deps in self.dependencies.items():
            if task_id in completed:
                continue

            if all(dep in completed for dep in deps):
                ready.append(self.tasks[task_id])

        return ready
def dependency_test():
    graph = NexusDependencyGraph()

    task_a = NexusTask("A", lambda: "A done")
    task_b = NexusTask("B", lambda: "B done")
    task_c = NexusTask("C", lambda: "C done")
    task_d = NexusTask("D", lambda: "D done")

    graph.add_task(task_a)
    graph.add_task(task_b)
    graph.add_task(task_c)
    graph.add_task(task_d)

    graph.add_dependency("B", "A")
    graph.add_dependency("C", "A")
    graph.add_dependency("D", "B")
    graph.add_dependency("D", "C")

    completed = set()

    print()
    print("NEXUS DEPENDENCY TEST")

    while len(completed) < len(graph.tasks):
        ready = graph.ready_tasks(completed)

        print("Ready:", [task.task_id for task in ready])

        for task in ready:
            print(task.task_id, "=>", task.run())
            completed.add(task.task_id)

    print("Completed:", sorted(completed))


dependency_test()
class NexusDependencyExecutor:
    def __init__(self, workers=4):
        self.workers = workers

    def execute(self, graph):
        completed = set()
        results = {}

        while len(completed) < len(graph.tasks):
            ready = graph.ready_tasks(completed)

            if not ready:
                raise RuntimeError("NEXUS detected a dependency cycle")

            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                future_results = list(
                    executor.map(
                        lambda task: (task.task_id, task.run()),
                        ready
                    )
                )

            for task_id, result in future_results:
                results[task_id] = result
                completed.add(task_id)

        return results
def dependency_parallel_test():
    graph = NexusDependencyGraph()

    graph.add_task(
        NexusTask("A", lambda: "A done")
    )

    graph.add_task(
        NexusTask("B", lambda: "B done")
    )

    graph.add_task(
        NexusTask("C", lambda: "C done")
    )

    graph.add_task(
        NexusTask("D", lambda: "D done")
    )

    graph.add_dependency("B", "A")
    graph.add_dependency("C", "A")
    graph.add_dependency("D", "B")
    graph.add_dependency("D", "C")

    executor = NexusDependencyExecutor(workers=4)

    results = executor.execute(graph)

    print()
    print("NEXUS DEPENDENCY PARALLEL TEST")

    for task_id, result in results.items():
        print(task_id, "=>", result)


dependency_parallel_test()
def nexus_timing_test():
    import time

    def work(seconds, name):
        time.sleep(seconds)
        return name

    # التنفيذ المتسلسل
    start = time.perf_counter()

    work(1, "A")
    work(1, "B")
    work(1, "C")
    work(1, "D")

    sequential_time = time.perf_counter() - start

    # بناء شبكة NEXUS
    graph = NexusDependencyGraph()

    graph.add_task(
        NexusTask("A", lambda: work(1, "A"))
    )

    graph.add_task(
        NexusTask("B", lambda: work(1, "B"))
    )

    graph.add_task(
        NexusTask("C", lambda: work(1, "C"))
    )

    graph.add_task(
        NexusTask("D", lambda: work(1, "D"))
    )

    graph.add_dependency("B", "A")
    graph.add_dependency("C", "A")
    graph.add_dependency("D", "B")
    graph.add_dependency("D", "C")

    executor = NexusDependencyExecutor(workers=4)

    start = time.perf_counter()

    executor.execute(graph)

    nexus_time = time.perf_counter() - start

    speedup = sequential_time / nexus_time

    print()
    print("NEXUS TIMING TEST")
    print(f"Sequential: {sequential_time:.3f} seconds")
    print(f"NEXUS:      {nexus_time:.3f} seconds")
    print(f"Speedup:    {speedup:.2f}x")


nexus_timing_test()
def nexus_real_performance_test():
    import time

    def cpu_work(n):
        total = 0

        for i in range(1, n):
            total += (i * i) % 1000003

        return total

    n = 1_000_000

    # التنفيذ المتسلسل
    start = time.perf_counter()

    sequential_results = []

    for _ in range(4):
        sequential_results.append(cpu_work(n))

    sequential_time = time.perf_counter() - start

    # NEXUS
    scheduler = NexusScheduler()

    for i in range(4):
        scheduler.submit(
            NexusTask(
                f"CPU-{i + 1}",
                lambda n=n: cpu_work(n)
            )
        )

    executor = NexusParallelExecutor(workers=4)

    start = time.perf_counter()

    nexus_results = executor.execute(scheduler)

    nexus_time = time.perf_counter() - start

    print()
    print("NEXUS REAL PERFORMANCE TEST")
    print(f"Sequential: {sequential_time:.3f} seconds")
    print(f"NEXUS:      {nexus_time:.3f} seconds")

    if nexus_time > 0:
        print(
            f"Speedup:    "
            f"{sequential_time / nexus_time:.2f}x"
        )

    print(
        "Results match:",
        all(
            result == sequential_results[i]
            for i, (_, result) in enumerate(nexus_results)
        )
    )


nexus_real_performance_test()
def nexus_worker_test():
    import time

    def cpu_work(n):
        total = 0

        for i in range(1, n):
            total += (i * i) % 1000003

        return total

    n = 1_000_000

    print()
    print("NEXUS WORKER SCALING TEST")

    for workers in [1, 2, 4, 8]:
        scheduler = NexusScheduler()

        for i in range(4):
            scheduler.submit(
                NexusTask(
                    f"TEST-{i + 1}",
                    lambda n=n: cpu_work(n)
                )
            )

        executor = NexusParallelExecutor(
            workers=workers
        )

        start = time.perf_counter()

        results = executor.execute(scheduler)

        elapsed = time.perf_counter() - start

        print(
            f"Workers: {workers} | "
            f"Time: {elapsed:.3f}s | "
            f"Results: {len(results)}"
        )


nexus_worker_test()
