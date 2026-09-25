import time
import nexus_unified_v2
from nexus_unified_v2 import NexusUnifiedV2
from nexus_game_workload_v1 import game_workload

nexus_unified_v2.FUNCTIONS["game"] = game_workload

COUNT = 10_000_000
REPEATS = 5

print("NEXUS 10M STABILITY TEST")
print("=" * 60)

for i in range(1, REPEATS + 1):

    start = time.perf_counter()
    direct_result = game_workload(COUNT)
    direct_time = time.perf_counter() - start

    runtime = NexusUnifiedV2(
        max_workers=4,
        exploration_repeats=1,
    )

    runtime.add_task(
        "GAME",
        "game",
        args=(COUNT,),
    )

    start = time.perf_counter()
    results = runtime.run()
    nexus_time = time.perf_counter() - start

    nexus_result = results["GAME"]

    correct = abs(direct_result - nexus_result) < 1e-6

    ratio = direct_time / nexus_time

    print()
    print(f"RUN: {i}")
    print(f"DIRECT: {direct_time:.6f}s")
    print(f"NEXUS:  {nexus_time:.6f}s")
    print(f"RATIO:  {ratio:.3f}x")
    print(f"CORRECT: {correct}")

print()
print("STABILITY TEST COMPLETE")
