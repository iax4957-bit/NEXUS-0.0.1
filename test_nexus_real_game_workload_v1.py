import time

import nexus_unified_v2
from nexus_unified_v2 import NexusUnifiedV2
from nexus_game_workload_v1 import game_workload

COUNT = 1000000

# تسجيل الحمل الجديد داخل NEXUS أثناء هذا الاختبار فقط
nexus_unified_v2.FUNCTIONS["game"] = game_workload

# التنفيذ المباشر
start = time.perf_counter()
direct_result = game_workload(COUNT)
direct_time = time.perf_counter() - start

# تنفيذ نفس الحمل عبر NEXUS
nexus = NexusUnifiedV2(
    max_workers=4,
    exploration_repeats=1,
)

nexus.add_task(
    "GAME",
    "game",
    args=(COUNT,),
)

start = time.perf_counter()
nexus_result = nexus.run()
nexus_time = time.perf_counter() - start

nexus_value = nexus_result["GAME"]

print()
print("NEXUS REAL GAME WORKLOAD V1")
print("=" * 60)
print("WORKLOAD:", COUNT)
print("DIRECT TIME:", f"{direct_time:.6f}s")
print("NEXUS TIME:", f"{nexus_time:.6f}s")
print("DIRECT RESULT:", direct_result)
print("NEXUS RESULT:", nexus_value)
print("RESULT CORRECT:", direct_result == nexus_value)
print("STATUS:", "PASS" if direct_result == nexus_value else "FAIL")
