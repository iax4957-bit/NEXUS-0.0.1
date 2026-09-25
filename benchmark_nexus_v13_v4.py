import statistics
import time
import os
import gc

from nexus_adaptive_runtime_v13 import NexusAdaptiveRuntimeV13


class Task:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        total = 0
        for i in range(self.value):
            total += (i * i) % 97
        return total


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPEATS = 5
WORK_VALUE = 3000
WORKERS = 2

MEMORY_FILE = os.path.join(
    BASE_DIR,
    "benchmark_v4_memory.json"
)

RELIABILITY_FILE = os.path.join(
    BASE_DIR,
    "benchmark_v4_reliability.json"
)


class BenchmarkRuntime(NexusAdaptiveRuntimeV13):

    def __init__(self):
        super().__init__(
            workers=WORKERS,
            batch_size=1000000,
            exploration_rate=0.0,
            memory_file=MEMORY_FILE,
            reliability_file=RELIABILITY_FILE
        )

    def _choose_backend(self, history, task_type):
        selected = {
            "backend": "PROCESS",
            "performance": None,
            "reliability": None,
            "confidence": 0.0,
            "samples": 0
        }

        decision = {
            "mode": "BENCHMARK",
            "backend": "PROCESS",
            "reason": "forced_process",
            "confidence": 0.0
        }

        return selected, decision


runtime = BenchmarkRuntime()


def make_tasks(count):
    return [
        Task(i, WORK_VALUE)
        for i in range(count)
    ]


def expected_results(tasks):
    return [
        (task.task_id, task.run())
        for task in tasks
    ]


def run_direct(tasks):
    start = time.perf_counter()

    results = [
        (task.task_id, task.run())
        for task in tasks
    ]

    elapsed = time.perf_counter() - start

    return elapsed, results


def run_process(tasks):
    runtime.cache_clear()

    start = time.perf_counter()

    result = runtime.execute(
        task_type="CPU",
        workload_size=len(tasks),
        tasks=tasks
    )

    elapsed = time.perf_counter() - start

    return elapsed, result["results"]


def benchmark_size(task_count):

    tasks = make_tasks(task_count)
    expected = expected_results(tasks)

    print()
    print("=" * 50)
    print("WORKLOAD:", task_count)
    print("=" * 50)
    print()

    # Warm-up
    run_direct(tasks)
    run_process(tasks)

    direct_times = []
    process_times = []

    print("DIRECT")
    print()

    for i in range(REPEATS):
        gc.collect()

        elapsed, results = run_direct(tasks)

        correct = results == expected
        direct_times.append(elapsed)

        print(
            "RUN",
            i + 1,
            "| TIME:",
            f"{elapsed:.6f}",
            "| RESULTS:",
            correct
        )

    print()
    print("PROCESS")
    print()

    for i in range(REPEATS):
        gc.collect()

        elapsed, results = run_process(tasks)

        correct = results == expected
        process_times.append(elapsed)

        print(
            "RUN",
            i + 1,
            "| TIME:",
            f"{elapsed:.6f}",
            "| RESULTS:",
            correct
        )

    direct_avg = statistics.mean(direct_times)
    process_avg = statistics.mean(process_times)

    direct_best = min(direct_times)
    process_best = min(process_times)

    direct_worst = max(direct_times)
    process_worst = max(process_times)

    speedup = (
        direct_avg / process_avg
        if process_avg > 0
        else 0
    )

    print()
    print("RESULTS")
    print()

    print(
        "DIRECT AVG:",
        f"{direct_avg:.6f}"
    )

    print(
        "PROCESS AVG:",
        f"{process_avg:.6f}"
    )

    print(
        "DIRECT BEST:",
        f"{direct_best:.6f}"
    )

    print(
        "PROCESS BEST:",
        f"{process_best:.6f}"
    )

    print(
        "DIRECT WORST:",
        f"{direct_worst:.6f}"
    )

    print(
        "PROCESS WORST:",
        f"{process_worst:.6f}"
    )

    print(
        "SPEEDUP:",
        f"{speedup:.3f}x"
    )

    print()

    return {
        "count": task_count,
        "direct": direct_avg,
        "process": process_avg,
        "speedup": speedup
    }


print("=== NEXUS V13 LARGE-SCALE BENCHMARK V4 ===")
print()
print("WORK VALUE:", WORK_VALUE)
print("WORKERS:", WORKERS)
print("REPEATS:", REPEATS)
print()

sizes = [
    100,
    500,
    1000,
    5000,
    10000
]

all_results = []

for size in sizes:
    all_results.append(
        benchmark_size(size)
    )

print()
print()
print("==================================================")
print("FINAL LARGE-SCALE SUMMARY")
print("==================================================")
print()

print(
    f"{'TASKS':>8} | "
    f"{'DIRECT':>12} | "
    f"{'PROCESS':>12} | "
    f"{'SPEEDUP':>10}"
)

print("-" * 52)

for item in all_results:
    print(
        f"{item['count']:>8} | "
        f"{item['direct']:>12.6f} | "
        f"{item['process']:>12.6f} | "
        f"{item['speedup']:>9.3f}x"
    )

print()
print("BENCHMARK COMPLETE: True")
print()
print("NOTE:")
print("This is a software benchmark on the same physical device.")
print("It does not claim that NEXUS exceeds the physical CPU itself.")
