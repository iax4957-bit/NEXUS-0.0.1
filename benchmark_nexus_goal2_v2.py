import os
import tempfile
import time

import nexus_unified_v2
from nexus_unified_v2 import NexusUnifiedV2, LearningMemory
from nexus_game_workload_v1 import game_workload


nexus_unified_v2.FUNCTIONS["game"] = game_workload


WORKLOADS = [
    10_000,
    1_000_000,
    10_000_000,
]

WARM_REPEATS = 5


def measure_direct(count):
    start = time.perf_counter()
    result = game_workload(count)
    elapsed = time.perf_counter() - start
    return result, elapsed


def build_nexus(count, memory):
    nexus = NexusUnifiedV2(
        max_workers=4,
        exploration_repeats=1,
    )

    nexus.memory = memory

    nexus.add_task(
        "GAME",
        "game",
        args=(count,),
    )

    return nexus


print("=" * 70)
print("NEXUS GOAL 2 BENCHMARK V2")
print("=" * 70)
print(f"WARM REPEATS: {WARM_REPEATS}")
print()


with tempfile.TemporaryDirectory() as tmp:

    memory_file = os.path.join(
        tmp,
        "goal2_memory.json",
    )

    for count in WORKLOADS:

        print("=" * 70)
        print(f"WORKLOAD: {count:,}")
        print("=" * 70)

        memory = LearningMemory(
            filename=memory_file
        )

        # ----------------------------------------------------
        # DIRECT REFERENCE
        # ----------------------------------------------------

        direct_value, direct_time = measure_direct(
            count
        )

        print(
            "DIRECT:",
            f"{direct_time:.6f}s"
        )

        # ----------------------------------------------------
        # COLD / EXPLORE
        # ----------------------------------------------------

        nexus_cold = build_nexus(
            count,
            memory,
        )

        start = time.perf_counter()

        cold_results = nexus_cold.run()

        cold_time = (
            time.perf_counter() - start
        )

        cold_value = cold_results["GAME"]

        print(
            "COLD NEXUS:",
            f"{cold_time:.6f}s"
        )

        print(
            "COLD CORRECT:",
            direct_value == cold_value
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
                count,
                memory,
            )

            start = time.perf_counter()

            warm_results = nexus_warm.run()

            warm_time = (
                time.perf_counter() - start
            )

            warm_value = warm_results["GAME"]

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

        print()
        print(
            "COLD RATIO:",
            f"{direct_time / cold_time:.3f}x"
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


print("=" * 70)
print("BENCHMARK V2 COMPLETE")
print("=" * 70)
