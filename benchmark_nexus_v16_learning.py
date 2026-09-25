import statistics
import time
import os
import gc

from nexus_adaptive_runtime_v16 import NexusAdaptiveRuntimeV16


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

WORKERS = [1, 2, 3, 4]


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


def nexus(tasks, size, memory_file, reliability_file, worker_memory_file):
    runtime = NexusAdaptiveRuntimeV16(
        workers=3,
        batch_size=1000000,
        exploration_rate=0.0,
        memory_file=memory_file,
        reliability_file=reliability_file,
        worker_memory_file=worker_memory_file
    )

    start = time.perf_counter()

    result = runtime.execute_adaptive(
        task_type="CPU",
        workload_size=size,
        tasks=tasks,
        worker_counts=WORKERS,
        learn_if_missing=True
    )

    elapsed = time.perf_counter() - start

    return elapsed, result


print("=== NEXUS V16 ADAPTIVE WORKER LEARNING ===")
print()
print("WORK VALUE:", WORK_VALUE)
print("REPEATS:", REPEATS)
print("WORKERS:", WORKERS)
print()

for size in SIZES:

    print()
    print("=" * 75)
    print("WORKLOAD:", size)
    print("=" * 75)

    tasks = make_tasks(size)

    expected = [
        (task.task_id, task.run())
        for task in tasks
    ]

    memory_file = os.path.join(
        BASE_DIR,
        f"benchmark_v16_memory_{size}.json"
    )

    reliability_file = os.path.join(
        BASE_DIR,
        f"benchmark_v16_reliability_{size}.json"
    )

    worker_memory_file = os.path.join(
        BASE_DIR,
        f"benchmark_v16_workers_{size}.json"
    )

    # -----------------------------
    # Direct baseline
    # -----------------------------

    direct_times = []

    direct(tasks)

    for _ in range(REPEATS):

        gc.collect()

        elapsed, results = direct(tasks)

        if results != expected:
            raise RuntimeError(
                f"DIRECT INCORRECT: size={size}"
            )

        direct_times.append(elapsed)

    direct_avg = statistics.mean(direct_times)

    print()
    print(
        "DIRECT AVG:",
        f"{direct_avg:.6f}"
    )

    # -----------------------------
    # NEXUS learning phase
    # -----------------------------

    first = nexus(
        tasks,
        size,
        memory_file,
        reliability_file,
        worker_memory_file
    )

    first_elapsed = first[0]
    first_result = first[1]

    if first_result["results"] != expected:
        raise RuntimeError(
            f"NEXUS LEARNING RESULT INCORRECT: size={size}"
        )

    print()
    print("LEARNING PHASE")
    print(
        "MODE:",
        first_result["mode"]
    )
    print(
        "SELECTED WORKERS:",
        first_result["workers"]
    )
    print(
        "ELAPSED:",
        f"{first_elapsed:.6f}"
    )
    print(
        "CORRECT:",
        first_result["correctness_checked"]
    )

    # -----------------------------
    # Learned execution
    # -----------------------------

    learned_times = []

    for _ in range(REPEATS):

        gc.collect()

        elapsed, result = nexus(
            tasks,
            size,
            memory_file,
            reliability_file,
            worker_memory_file
        )

        if result["results"] != expected:
            raise RuntimeError(
                f"NEXUS LEARNED RESULT INCORRECT: size={size}"
            )

        learned_times.append(elapsed)

    learned_avg = statistics.mean(learned_times)

    speedup = (
        direct_avg / learned_avg
        if learned_avg > 0
        else 0
    )

    print()
    print("LEARNED EXECUTION")
    print(
        "MODE:",
        result["mode"]
    )
    print(
        "WORKERS:",
        result["workers"]
    )
    print(
        "AVG:",
        f"{learned_avg:.6f}"
    )
    print(
        "BEST:",
        f"{min(learned_times):.6f}"
    )
    print(
        "SPEEDUP:",
        f"{speedup:.3f}x"
    )
    print(
        "ALL RESULTS CORRECT:",
        True
    )


print()
print("=" * 75)
print("V16 BENCHMARK COMPLETE: True")
print("=" * 75)
print()
print("NEXUS V16 learns worker count from measurements.")
print("Only configurations producing correct results are accepted.")
print("Speedup is measured against direct sequential execution.")
