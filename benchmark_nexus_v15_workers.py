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

WORK_VALUE = 3000
REPEATS = 5

SIZES = [
    500,
    1000,
    5000,
    10000
]

WORKER_COUNTS = [
    1,
    2,
    3,
    4
]


class WorkerBenchmarkRuntime(NexusAdaptiveRuntimeV13):

    def __init__(self, workers):
        memory_file = os.path.join(
            BASE_DIR,
            f"benchmark_v15_memory_{workers}.json"
        )

        reliability_file = os.path.join(
            BASE_DIR,
            f"benchmark_v15_reliability_{workers}.json"
        )

        super().__init__(
            workers=workers,
            batch_size=1000000,
            exploration_rate=0.0,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

        self.forced_backend = "PROCESS"

    def _choose_backend(self, history, task_type):
        selected = {
            "backend": self.forced_backend,
            "performance": None,
            "reliability": None,
            "confidence": 1.0,
            "samples": 100
        }

        decision = {
            "mode": "WORKER_BENCHMARK",
            "backend": self.forced_backend,
            "reason": "forced_process",
            "confidence": 1.0
        }

        return selected, decision


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

    elapsed = time.perf_counter() - start

    return elapsed, results


def process(runtime, tasks):
    start = time.perf_counter()

    result = runtime.execute(
        task_type="CPU",
        workload_size=len(tasks),
        tasks=tasks
    )

    elapsed = time.perf_counter() - start

    return elapsed, result["results"]


def benchmark_worker(size, workers):

    tasks = make_tasks(size)

    expected = [
        (task.task_id, task.run())
        for task in tasks
    ]

    runtime = WorkerBenchmarkRuntime(workers)

    # Warm-up
    direct(tasks)
    process(runtime, tasks)

    times = []

    for _ in range(REPEATS):

        gc.collect()

        elapsed, results = process(
            runtime,
            tasks
        )

        if results != expected:
            raise RuntimeError(
                f"Incorrect results: size={size}, workers={workers}"
            )

        times.append(elapsed)

    return {
        "average": statistics.mean(times),
        "best": min(times),
        "worst": max(times),
        "times": times
    }


print("=== NEXUS V15 WORKER SCALING BENCHMARK ===")
print()
print("WORK VALUE:", WORK_VALUE)
print("REPEATS:", REPEATS)
print("WORKER COUNTS:", WORKER_COUNTS)
print()

final_results = {}

for size in SIZES:

    tasks = make_tasks(size)

    expected = [
        (task.task_id, task.run())
        for task in tasks
    ]

    direct_times = []

    # Direct baseline
    direct(tasks)

    for _ in range(REPEATS):

        gc.collect()

        elapsed, results = direct(tasks)

        if results != expected:
            raise RuntimeError(
                f"Direct results incorrect: size={size}"
            )

        direct_times.append(elapsed)

    direct_avg = statistics.mean(direct_times)

    print()
    print("=" * 70)
    print("WORKLOAD:", size)
    print("=" * 70)
    print()
    print(
        "DIRECT AVG:",
        f"{direct_avg:.6f}"
    )
    print()

    final_results[size] = {
        "direct": direct_avg,
        "workers": {}
    }

    for workers in WORKER_COUNTS:

        result = benchmark_worker(
            size,
            workers
        )

        average = result["average"]

        speedup = (
            direct_avg / average
            if average > 0
            else 0
        )

        final_results[size]["workers"][workers] = {
            "average": average,
            "best": result["best"],
            "worst": result["worst"],
            "speedup": speedup
        }

        print(
            "WORKERS:",
            workers,
            "| AVG:",
            f"{average:.6f}",
            "| BEST:",
            f"{result['best']:.6f}",
            "| SPEEDUP:",
            f"{speedup:.3f}x"
        )

    best_workers = min(
        final_results[size]["workers"],
        key=lambda w:
            final_results[size]["workers"][w]["average"]
    )

    best_data = final_results[size]["workers"][
        best_workers
    ]

    print()
    print(
        "BEST WORKERS:",
        best_workers
    )

    print(
        "BEST SPEEDUP:",
        f"{best_data['speedup']:.3f}x"
    )


print()
print()
print("=" * 75)
print("FINAL WORKER SCALING SUMMARY")
print("=" * 75)
print()

print(
    f"{'TASKS':>8} | "
    f"{'DIRECT':>10} | "
    f"{'W1':>10} | "
    f"{'W2':>10} | "
    f"{'W3':>10} | "
    f"{'W4':>10} | "
    f"{'BEST':>6}"
)

print("-" * 75)

for size in SIZES:

    data = final_results[size]

    best_workers = min(
        data["workers"],
        key=lambda w:
            data["workers"][w]["average"]
    )

    print(
        f"{size:>8} | "
        f"{data['direct']:>10.4f} | "
        f"{data['workers'][1]['average']:>10.4f} | "
        f"{data['workers'][2]['average']:>10.4f} | "
        f"{data['workers'][3]['average']:>10.4f} | "
        f"{data['workers'][4]['average']:>10.4f} | "
        f"{best_workers:>6}"
    )

print()
print("BENCHMARK COMPLETE: True")
print()
print("NOTE:")
print("This measures PROCESS worker scaling on the same device.")
print("It does not claim NEXUS exceeds the physical CPU.")
