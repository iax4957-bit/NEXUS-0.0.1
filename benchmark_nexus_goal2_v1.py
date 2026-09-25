import time
import nexus_unified_v2
from nexus_unified_v2 import NexusUnifiedV2
from nexus_game_workload_v1 import game_workload


nexus_unified_v2.FUNCTIONS["game"] = game_workload


WORKLOADS = [
    10_000,
    1_000_000,
    10_000_000,
]

REPEATS = 5


def measure_direct(count):
    start = time.perf_counter()
    result = game_workload(count)
    elapsed = time.perf_counter() - start
    return result, elapsed


def measure_nexus(count):
    nexus = NexusUnifiedV2(
        max_workers=4,
        exploration_repeats=1,
    )

    nexus.add_task(
        "GAME",
        "game",
        args=(count,),
    )

    start = time.perf_counter()
    results = nexus.run()
    elapsed = time.perf_counter() - start

    return results["GAME"], elapsed


print("=" * 70)
print("NEXUS GOAL 2 BENCHMARK V1")
print("=" * 70)
print(f"REPEATS: {REPEATS}")
print()

for count in WORKLOADS:

    print("=" * 70)
    print(f"WORKLOAD: {count:,}")
    print("=" * 70)

    direct_times = []
    nexus_times = []

    # --------------------------------------------------------
    # WARM-UP
    # --------------------------------------------------------

    direct_value, _ = measure_direct(count)
    nexus_value, _ = measure_nexus(count)

    correct = direct_value == nexus_value

    print("CORRECT:", correct)
    print()

    if not correct:
        print("STATUS: FAIL")
        continue

    # --------------------------------------------------------
    # MEASUREMENTS
    # --------------------------------------------------------

    for run in range(1, REPEATS + 1):

        direct_value, direct_time = measure_direct(count)
        nexus_value, nexus_time = measure_nexus(count)

        correct = direct_value == nexus_value

        direct_times.append(direct_time)
        nexus_times.append(nexus_time)

        ratio = (
            direct_time / nexus_time
            if nexus_time > 0
            else 0
        )

        print(
            f"RUN {run}: "
            f"DIRECT={direct_time:.6f}s | "
            f"NEXUS={nexus_time:.6f}s | "
            f"RATIO={ratio:.3f}x | "
            f"CORRECT={correct}"
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    direct_avg = sum(direct_times) / len(direct_times)
    nexus_avg = sum(nexus_times) / len(nexus_times)

    avg_ratio = (
        direct_avg / nexus_avg
        if nexus_avg > 0
        else 0
    )

    print()
    print("DIRECT AVG:", f"{direct_avg:.6f}s")
    print("NEXUS AVG: ", f"{nexus_avg:.6f}s")
    print("AVG RATIO: ", f"{avg_ratio:.3f}x")

    if avg_ratio > 1:
        print("AVERAGE: NEXUS FASTER")
    elif avg_ratio < 1:
        print("AVERAGE: NEXUS SLOWER")
    else:
        print("AVERAGE: EQUAL")

print()
print("=" * 70)
print("BENCHMARK COMPLETE")
print("=" * 70)
