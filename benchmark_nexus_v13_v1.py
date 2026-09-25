import statistics
import time

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


class BenchmarkRuntime(NexusAdaptiveRuntimeV13):

    def __init__(self):
        super().__init__(
            workers=2,
            batch_size=10,
            exploration_rate=0.0,
            memory_file="/tmp/nexus_benchmark_memory.json",
            reliability_file="/tmp/nexus_benchmark_reliability.json"
        )

    def _execute_backend(self, backend, tasks):
        return [
            (task.task_id, task.run())
            for task in tasks
        ]


TASK_COUNT = 100
REPEATS = 5
WORK_VALUE = 3000

tasks = [
    Task(i, WORK_VALUE)
    for i in range(TASK_COUNT)
]

expected = [
    (task.task_id, task.run())
    for task in tasks
]


def run_baseline():
    start = time.perf_counter()

    results = [
        (task.task_id, task.run())
        for task in tasks
    ]

    elapsed = time.perf_counter() - start

    return elapsed, results


runtime = BenchmarkRuntime()


def run_nexus():
    runtime.cache_clear()

    start = time.perf_counter()

    result = runtime.execute_auto_batched_cached(
        workload_size=TASK_COUNT,
        tasks=tasks,
        cpu_ratio=0.95,
        io_ratio=0.05
    )

    elapsed = time.perf_counter() - start

    return elapsed, result["results"]


print("=== NEXUS V13 REAL BENCHMARK V1 ===")
print()
print("TASK COUNT:", TASK_COUNT)
print("WORK VALUE:", WORK_VALUE)
print("REPEATS:", REPEATS)
print()

baseline_times = []
nexus_times = []

# Warm-up
run_baseline()
run_nexus()

print("BASELINE RUNS")
print()

for i in range(REPEATS):
    elapsed, results = run_baseline()

    correct = results == expected

    baseline_times.append(elapsed)

    print(
        "RUN",
        i + 1,
        "| TIME:",
        f"{elapsed:.6f}",
        "| RESULTS:",
        correct
    )

print()
print("NEXUS RUNS")
print()

for i in range(REPEATS):
    elapsed, results = run_nexus()

    correct = results == expected

    nexus_times.append(elapsed)

    print(
        "RUN",
        i + 1,
        "| TIME:",
        f"{elapsed:.6f}",
        "| RESULTS:",
        correct
    )

baseline_avg = statistics.mean(baseline_times)
nexus_avg = statistics.mean(nexus_times)

baseline_best = min(baseline_times)
nexus_best = min(nexus_times)

speedup = (
    baseline_avg / nexus_avg
    if nexus_avg > 0
    else 0
)

print()
print("=== RESULTS ===")
print()
print("BASELINE AVERAGE:", f"{baseline_avg:.6f}")
print("NEXUS AVERAGE:", f"{nexus_avg:.6f}")
print("BASELINE BEST:", f"{baseline_best:.6f}")
print("NEXUS BEST:", f"{nexus_best:.6f}")
print("SPEEDUP BASELINE/NEXUS:", f"{speedup:.3f}x")
print()

baseline_correct = all(
    run_baseline()[1] == expected
    for _ in range(1)
)

nexus_correct = all(
    result == expected
    for result in [
        run_nexus()[1]
    ]
)

print("BASELINE RESULTS CORRECT:", baseline_correct)
print("NEXUS RESULTS CORRECT:", nexus_correct)
print()

print("NOTE:")
print("This benchmark compares software execution paths on the same phone.")
print("It does not claim that NEXUS is faster than the physical CPU itself.")
print()
print("BENCHMARK COMPLETE: True")
