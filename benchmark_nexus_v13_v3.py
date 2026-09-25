import statistics
import time
import os

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

TASK_COUNT = 100
REPEATS = 5
WORK_VALUE = 3000
WORKERS = 2

MEMORY_FILE = os.path.join(
    BASE_DIR,
    "benchmark_v3_memory.json"
)

RELIABILITY_FILE = os.path.join(
    BASE_DIR,
    "benchmark_v3_reliability.json"
)


def make_tasks():
    return [
        Task(i, WORK_VALUE)
        for i in range(TASK_COUNT)
    ]


tasks = make_tasks()

expected = [
    (task.task_id, task.run())
    for task in tasks
]


def execute_direct():
    return [
        (task.task_id, task.run())
        for task in tasks
    ]


def run_direct():
    start = time.perf_counter()
    results = execute_direct()
    elapsed = time.perf_counter() - start
    return elapsed, results


class RealBenchmarkRuntime(NexusAdaptiveRuntimeV13):

    def __init__(self, backend):
        super().__init__(
            workers=WORKERS,
            batch_size=TASK_COUNT,
            exploration_rate=0.0,
            memory_file=MEMORY_FILE,
            reliability_file=RELIABILITY_FILE
        )
        self.forced_backend = backend

    def _choose_backend(self, history, task_type):
        selected = {
            "backend": self.forced_backend,
            "performance": None,
            "reliability": None,
            "confidence": 0.0,
            "samples": 0
        }

        learning_decision = {
            "mode": "BENCHMARK",
            "backend": self.forced_backend,
            "reason": "forced_backend",
            "confidence": 0.0
        }

        return selected, learning_decision


def run_nexus(backend):
    runtime = RealBenchmarkRuntime(backend)

    runtime.cache_clear()

    start = time.perf_counter()

    result = runtime.execute(
        task_type="CPU",
        workload_size=TASK_COUNT,
        tasks=tasks
    )

    elapsed = time.perf_counter() - start

    return elapsed, result["results"]


def benchmark_method(name, function):
    times = []

    print(name)
    print()

    # Warm-up
    function()

    for i in range(REPEATS):
        elapsed, results = function()

        correct = results == expected
        times.append(elapsed)

        print(
            "RUN",
            i + 1,
            "| TIME:",
            f"{elapsed:.6f}",
            "| RESULTS:",
            correct
        )

    average = statistics.mean(times)
    best = min(times)

    print()
    print("AVERAGE:", f"{average:.6f}")
    print("BEST:", f"{best:.6f}")
    print()

    return average, best


print("=== NEXUS V13 REAL BACKEND BENCHMARK V3 ===")
print()
print("TASK COUNT:", TASK_COUNT)
print("WORK VALUE:", WORK_VALUE)
print("WORKERS:", WORKERS)
print("REPEATS:", REPEATS)
print()

results = {}

results["DIRECT"] = benchmark_method(
    "1. DIRECT / SEQUENTIAL",
    run_direct
)

results["SEQUENTIAL"] = benchmark_method(
    "2. NEXUS + SEQUENTIAL",
    lambda: run_nexus("SEQUENTIAL")
)

results["THREAD"] = benchmark_method(
    "3. NEXUS + THREAD",
    lambda: run_nexus("THREAD")
)

results["PROCESS"] = benchmark_method(
    "4. NEXUS + PROCESS",
    lambda: run_nexus("PROCESS")
)


direct_avg = results["DIRECT"][0]

print("=== SPEEDUPS VS DIRECT ===")
print()

for name in ["SEQUENTIAL", "THREAD", "PROCESS"]:
    avg = results[name][0]

    speedup = (
        direct_avg / avg
        if avg > 0
        else 0
    )

    print(
        name,
        "SPEEDUP:",
        f"{speedup:.3f}x"
    )

print()

print("=== BEST TIMES ===")
print()

for name, values in results.items():
    print(
        name,
        "| BEST:",
        f"{values[1]:.6f}"
    )

print()

print("IMPORTANT:")
print("This measures software execution paths on the same physical CPU.")
print("It does NOT mean NEXUS replaces or exceeds the physical CPU.")
print()

print("BENCHMARK COMPLETE: True")
