from nexus_game_workload_v1 import game_workload
import time
import concurrent.futures

COUNT = 10000
JOBS = 4

def run_job(_):
    return game_workload(COUNT)

# التنفيذ المباشر
start = time.perf_counter()
direct_results = [run_job(i) for i in range(JOBS)]
direct_time = time.perf_counter() - start

# تنفيذ متوازٍ — النموذج الذي سنبني عليه NEXUS
start = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=JOBS) as executor:
    nexus_results = list(executor.map(run_job, range(JOBS)))

nexus_time = time.perf_counter() - start

correct = direct_results == nexus_results

print("NEXUS GAME WORKLOAD V1")
print("=" * 50)
print("WORKLOAD PER JOB:", COUNT)
print("JOBS:", JOBS)
print("DIRECT TIME:", f"{direct_time:.6f}s")
print("NEXUS-STYLE TIME:", f"{nexus_time:.6f}s")
print("RESULTS CORRECT:", correct)
print("RESULT:", nexus_results[0])
print("STATUS:", "PASS" if correct else "FAIL")
