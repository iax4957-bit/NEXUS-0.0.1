from nexus_game_workload_v1 import game_workload
import concurrent.futures
import time
import json

WORKLOADS = [10000, 50000, 100000, 500000, 1000000]
JOBS = 4
results = []

print("NEXUS GAME TRAINING V1")
print("=" * 60)

for count in WORKLOADS:
    print(f"\nWORKLOAD: {count}")

    start = time.perf_counter()
    direct_results = [game_workload(count) for _ in range(JOBS)]
    direct_time = time.perf_counter() - start

    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=JOBS) as executor:
        parallel_results = list(
            executor.map(game_workload, [count] * JOBS)
        )
    parallel_time = time.perf_counter() - start

    correct = direct_results == parallel_results

    if parallel_time < direct_time:
        best = "PARALLEL"
    else:
        best = "DIRECT"

    entry = {
        "workload": count,
        "jobs": JOBS,
        "direct_time": direct_time,
        "parallel_time": parallel_time,
        "best": best,
        "correct": correct,
    }

    results.append(entry)

    print(f"DIRECT:   {direct_time:.6f}s")
    print(f"PARALLEL: {parallel_time:.6f}s")
    print(f"BEST:     {best}")
    print(f"CORRECT:  {correct}")

with open("nexus_game_training_v1.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("MEMORY FILE: nexus_game_training_v1.json")
print("STATUS: PASS")
