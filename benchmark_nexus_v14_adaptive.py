import statistics
import time
import os
import json

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

MEMORY_FILE = os.path.join(
    BASE_DIR,
    "benchmark_v14_memory.json"
)

RELIABILITY_FILE = os.path.join(
    BASE_DIR,
    "benchmark_v14_reliability.json"
)

WORK_VALUE = 3000
WORKERS = 2
REPEATS = 5

SIZES = [
    100,
    500,
    1000,
    5000,
    10000
]


def make_tasks(count):
    return [
        Task(i, WORK_VALUE)
        for i in range(count)
    ]


def direct(tasks):
    start = time.perf_counter()

    results = [
        (task.task_id, task.run())
        for task in tasks
    ]

    return time.perf_counter() - start, results


class ForcedRuntime(NexusAdaptiveRuntimeV13):

    def __init__(self, backend):
        super().__init__(
            workers=WORKERS,
            batch_size=1000000,
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
            "confidence": 1.0,
            "samples": 100
        }

        decision = {
            "mode": "TRAINING",
            "backend": self.forced_backend,
            "reason": "benchmark_training",
            "confidence": 1.0
        }

        return selected, decision


def nexus_forced(backend, tasks):
    runtime = ForcedRuntime(backend)

    start = time.perf_counter()

    result = runtime.execute(
        task_type="CPU",
        workload_size=len(tasks),
        tasks=tasks
    )

    elapsed = time.perf_counter() - start

    return elapsed, result["results"]


class AdaptiveRuntime(NexusAdaptiveRuntimeV13):

    def __init__(self):
        super().__init__(
            workers=WORKERS,
            batch_size=1000000,
            exploration_rate=0.0,
            memory_file=MEMORY_FILE,
            reliability_file=RELIABILITY_FILE
        )


def adaptive_run(runtime, tasks):
    start = time.perf_counter()

    result = runtime.execute(
        task_type="CPU",
        workload_size=len(tasks),
        tasks=tasks
    )

    elapsed = time.perf_counter() - start

    return elapsed, result


def train_size(size):

    tasks = make_tasks(size)

    print()
    print("=" * 60)
    print("TRAINING WORKLOAD:", size)
    print("=" * 60)

    measurements = {}

    for backend in [
        "SEQUENTIAL",
        "PROCESS"
    ]:

        times = []

        # Warm-up
        nexus_forced(backend, tasks)

        for _ in range(3):
            elapsed, results = nexus_forced(
                backend,
                tasks
            )

            expected = [
                (task.task_id, task.run())
                for task in tasks
            ]

            if results != expected:
                raise RuntimeError(
                    f"Incorrect results during training: {backend}"
                )

            times.append(elapsed)

        average = statistics.mean(times)

        measurements[backend] = average

        print(
            backend,
            "AVG:",
            f"{average:.6f}"
        )

    best = min(
        measurements,
        key=measurements.get
    )

    print(
        "TRAINING WINNER:",
        best
    )

    return measurements


print("=== NEXUS V14 ADAPTIVE LEARNING BENCHMARK ===")
print()
print("This benchmark trains NEXUS using real measurements.")
print("No benchmark result is manually inserted.")
print()

# Start clean.
for filename in [
    MEMORY_FILE,
    RELIABILITY_FILE
]:
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


# ============================================================
# PHASE 1: REAL TRAINING
# ============================================================

training = {}

for size in SIZES:
    training[size] = train_size(size)


# ============================================================
# PHASE 2: ADAPTIVE EVALUATION
# ============================================================

runtime = AdaptiveRuntime()

print()
print()
print("=" * 60)
print("ADAPTIVE NEXUS EVALUATION")
print("=" * 60)

summary = []

for size in SIZES:

    tasks = make_tasks(size)

    expected = [
        (task.task_id, task.run())
        for task in tasks
    ]

    direct_times = []
    nexus_times = []
    selected_backends = []

    # Warm-up
    direct(tasks)
    adaptive_run(runtime, tasks)

    for run in range(REPEATS):

        elapsed_direct, direct_results = direct(tasks)

        if direct_results != expected:
            raise RuntimeError(
                "Direct results incorrect"
            )

        direct_times.append(
            elapsed_direct
        )

        elapsed_nexus, result = adaptive_run(
            runtime,
            tasks
        )

        if result["results"] != expected:
            raise RuntimeError(
                "NEXUS results incorrect"
            )

        nexus_times.append(
            elapsed_nexus
        )

        selected_backends.append(
            result["backend"]
        )

        print(
            "SIZE:",
            size,
            "| RUN:",
            run + 1,
            "| NEXUS:",
            result["backend"],
            "| DIRECT:",
            f"{elapsed_direct:.6f}",
            "| NEXUS:",
            f"{elapsed_nexus:.6f}"
        )

    direct_avg = statistics.mean(
        direct_times
    )

    nexus_avg = statistics.mean(
        nexus_times
    )

    speedup = (
        direct_avg / nexus_avg
        if nexus_avg > 0
        else 0
    )

    summary.append({
        "size": size,
        "direct": direct_avg,
        "nexus": nexus_avg,
        "speedup": speedup,
        "backends": selected_backends
    })


print()
print()
print("=" * 70)
print("FINAL V14 RESULT")
print("=" * 70)
print()

print(
    f"{'TASKS':>8} | "
    f"{'DIRECT':>12} | "
    f"{'NEXUS':>12} | "
    f"{'SPEEDUP':>10} | "
    f"{'BACKEND':>12}"
)

print("-" * 70)

for item in summary:

    backend = max(
        set(item["backends"]),
        key=item["backends"].count
    )

    print(
        f"{item['size']:>8} | "
        f"{item['direct']:>12.6f} | "
        f"{item['nexus']:>12.6f} | "
        f"{item['speedup']:>9.3f}x | "
        f"{backend:>12}"
    )

print()
print("ADAPTIVE DECISION CHECK")
print()

for item in summary:
    print(
        item["size"],
        "->",
        item["backends"]
    )

print()
print("BENCHMARK COMPLETE: True")
