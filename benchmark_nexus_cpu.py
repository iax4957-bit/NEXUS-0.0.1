import time
from nexus_unified_v2 import NexusUnifiedV2, cpu_work

TASKS = 4
VALUE = 50

print("=" * 60)
print("NEXUS CPU BENCHMARK")
print("=" * 60)
print(f"TASKS: {TASKS}")
print(f"VALUE: {VALUE}")
print()

# ------------------------------------------------------------
# DIRECT
# ------------------------------------------------------------

start = time.perf_counter()

direct_results = [
    cpu_work(VALUE)
    for _ in range(TASKS)
]

direct_time = time.perf_counter() - start

# ------------------------------------------------------------
# NEXUS
# ------------------------------------------------------------

nexus = NexusUnifiedV2(
    max_workers=4,
    exploration_repeats=1,
)

for i in range(TASKS):
    nexus.add_task(
        f"T{i}",
        "cpu",
        args=(VALUE,),
    )

start = time.perf_counter()

nexus_results = nexus.run()

nexus_time = time.perf_counter() - start

# ------------------------------------------------------------
# VALIDATION
# ------------------------------------------------------------

direct_values = list(direct_results)
nexus_values = [
    nexus_results[f"T{i}"]
    for i in range(TASKS)
]

correct = direct_values == nexus_values

print("DIRECT TIME:", f"{direct_time:.6f}s")
print("NEXUS TIME:", f"{nexus_time:.6f}s")
print("DIRECT RESULTS:", direct_values)
print("NEXUS RESULTS:", nexus_values)
print("RESULTS CORRECT:", correct)

if nexus_time > 0:
    print(
        "TIME RATIO:",
        f"{direct_time / nexus_time:.3f}x"
    )

print("STATUS:", "PASS" if correct else "FAIL")
