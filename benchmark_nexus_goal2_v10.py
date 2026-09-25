import os
import tempfile
import time

import nexus_unified_v2
from nexus_unified_v2 import NexusUnifiedV2, LearningMemory



WORKLOADS = [
    {
        "name": "CPU-4TASK-320K",
        "operation": "cpu",
        "args": (50, 320_000),
        "tasks": 4,
        "direct": None,
    },
    {
        "name": "CPU-4TASK-20K",
        "operation": "cpu",
        "args": (50, 20_000),
        "tasks": 4,
        "direct": None,
    },
    {
        "name": "CPU-4TASK-160K",
        "operation": "cpu",
        "args": (50, 160_000),
        "tasks": 4,
        "direct": None,
    },
    {
        "name": "CPU-4TASK-80K",
        "operation": "cpu",
        "args": (50, 80_000),
        "tasks": 4,
        "direct": None,
    },
]

WARM_REPEATS = 5

# V9 PATTERN TEST
WORKLOADS.append(
    {
        "name": "CPU-1TASK-80K",
        "operation": "cpu",
        "args": (50, 80_000),
        "tasks": 1,
        "direct": None,
    }
)



def measure_cpu_direct(args, tasks):
    start = time.perf_counter()

    results = [
        nexus_unified_v2.cpu_work(*args)
        for _ in range(tasks)
    ]

    elapsed = time.perf_counter() - start

    return (
        results[0] if tasks == 1 else results,
        elapsed,
    )


def build_nexus(case, memory):
    nexus = NexusUnifiedV2(
        max_workers=4,
        exploration_repeats=1,
    )

    nexus.memory = memory

    tasks = case.get("tasks", 1)

    for i in range(tasks):
        nexus.add_task(
            f"T{i}",
            case["operation"],
            args=case["args"],
        )

    return nexus


def measure_case_direct(case):
    if case["operation"] == "game":
        return measure_game_direct(
            case["args"]
        )

    if case["operation"] == "cpu":
        return measure_cpu_direct(
            case["args"],
            case["tasks"],
        )

    raise ValueError(
        f"Unknown operation: {case['operation']}"
    )


def extract_nexus_value(case, results):
    tasks = case.get("tasks", 1)

    if tasks == 1:
        return results["T0"]

    return [
        results[f"T{i}"]
        for i in range(tasks)
    ]


print("=" * 70)
print("NEXUS GOAL 2 BENCHMARK V3")
print("MULTI-WORKLOAD")
print("=" * 70)
print(f"WARM REPEATS: {WARM_REPEATS}")
print()


memory_file = os.path.join(
    os.path.dirname(__file__),
    "nexus_goal2_v10_memory.json",
)

for case in WORKLOADS:

    memory = LearningMemory(
        filename=memory_file
    )

    print("=" * 70)
    print(f"WORKLOAD: {case['name']}")
    print("=" * 70)

    # ----------------------------------------------------
    # DIRECT REFERENCE
    # ----------------------------------------------------

    direct_value, direct_time = (
        measure_case_direct(case)
    )

    print(
        "DIRECT:",
        f"{direct_time:.6f}s"
    )

    # ----------------------------------------------------
    # COLD / EXPLORE
    # ----------------------------------------------------

    nexus_cold = build_nexus(
        case,
        memory,
    )

    start = time.perf_counter()

    cold_results = nexus_cold.run()

    cold_time = (
        time.perf_counter() - start
    )

    cold_value = extract_nexus_value(
        case,
        cold_results,
    )

    cold_correct = (
        direct_value == cold_value
    )

    print(
        "COLD NEXUS:",
        f"{cold_time:.6f}s"
    )

    print(
        "COLD CORRECT:",
        cold_correct
    )

    # ----------------------------------------------------
    # WARM / EXPLOIT
    # ----------------------------------------------------

    warm_times = []

    print()

    for run in range(
        1,
        WARM_REPEATS + 1,
    ):

        nexus_warm = build_nexus(
            case,
            memory,
        )

        start = time.perf_counter()

        warm_results = nexus_warm.run()

        warm_time = (
            time.perf_counter()
            - start
        )

        warm_value = extract_nexus_value(
            case,
            warm_results,
        )

        correct = (
            direct_value == warm_value
        )

        warm_times.append(warm_time)

        ratio = (
            direct_time / warm_time
            if warm_time > 0
            else 0
        )

        print(
            f"WARM RUN {run}: "
            f"NEXUS={warm_time:.6f}s | "
            f"RATIO={ratio:.3f}x | "
            f"CORRECT={correct}"
        )

    warm_avg = (
        sum(warm_times)
        / len(warm_times)
    )

    warm_ratio = (
        direct_time / warm_avg
        if warm_avg > 0
        else 0
    )

    cold_ratio = (
        direct_time / cold_time
        if cold_time > 0
        else 0
    )

    print()
    print(
        "COLD RATIO:",
        f"{cold_ratio:.3f}x"
    )

    print(
        "WARM AVG:",
        f"{warm_avg:.6f}s"
    )

    print(
        "WARM RATIO:",
        f"{warm_ratio:.3f}x"
    )

    if warm_ratio > 1:
        print(
            "WARM RESULT: NEXUS FASTER"
        )
    elif warm_ratio < 1:
        print(
            "WARM RESULT: NEXUS SLOWER"
        )
    else:
        print(
            "WARM RESULT: EQUAL"
        )

        print()


# ============================================================
# V8 REVISIT TEST
# Revisit learned workloads after all workloads were explored.
# ============================================================

print("=" * 70)
print("V8 REVISIT TEST")
print("REVISIT: 320K -> 20K")
print("=" * 70)

for revisit_name in (
    "CPU-4TASK-320K",
    "CPU-4TASK-20K",
):
    revisit_case = next(
        case
        for case in WORKLOADS
        if case["name"] == revisit_name
    )

    revisit_memory = LearningMemory(
        filename=memory_file
    )

    print()
    print("REVISIT WORKLOAD:", revisit_name)

    revisit_nexus = build_nexus(
        revisit_case,
        revisit_memory,
    )

    revisit_start = time.perf_counter()

    revisit_results = revisit_nexus.run()

    revisit_elapsed = (
        time.perf_counter()
        - revisit_start
    )

    revisit_value = extract_nexus_value(
        revisit_case,
        revisit_results,
    )

    expected_value = measure_cpu_direct(
        revisit_case["args"],
        revisit_case["tasks"],
    )[0]

    print(
        "REVISIT TIME:",
        f"{revisit_elapsed:.6f}s"
    )

    print(
        "REVISIT CORRECT:",
        revisit_value == expected_value
    )


print("=" * 70)
