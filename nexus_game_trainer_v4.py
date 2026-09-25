import json
import time

import nexus_unified_v2
from nexus_unified_v2 import NexusUnifiedV2
from nexus_game_workload_v1 import game_workload


MEMORY_FILE = "nexus_game_memory_v3.json"

WORKLOADS = [
    10000,
]


nexus_unified_v2.FUNCTIONS["game"] = game_workload


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


memory = load_memory()

print("NEXUS GAME TRAINER V2")
print("=" * 60)
print("MEMORY:", MEMORY_FILE)


for count in WORKLOADS:

    print()
    print("WORKLOAD:", count)

    # مرجع مباشر
    start = time.perf_counter()
    direct_result = game_workload(count)
    direct_time = time.perf_counter() - start

    # NEXUS
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
    nexus_result = nexus.run()
    nexus_time = time.perf_counter() - start

    nexus_value = nexus_result["GAME"]

    correct = direct_result == nexus_value

    entry = {
        "workload": count,
        "direct_time": direct_time,
        "nexus_time": nexus_time,
        "correct": correct,
        "direct_result": direct_result,
        "nexus_result": nexus_value,
    }

    memory.append(entry)

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

    print("DIRECT:", f"{direct_time:.6f}s")
    print("NEXUS:", f"{nexus_time:.6f}s")
    print("CORRECT:", correct)
    print("MEMORY SAVED")


print()
print("=" * 60)
print("TRAINING COMPLETE")
print("TOTAL EXPERIENCES:", len(memory))
print("MEMORY FILE:", MEMORY_FILE)
print("STATUS: PASS")
