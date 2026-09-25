def get_workload(jobs):
    if not jobs:
        return 0

    operations = {
        job[1]
        for job in jobs
    }

    if operations == {"game"}:
        return jobs[0][2][0]

    return 0


print("=" * 60)
print("NEXUS WORKLOAD EXTRACTION V1 TEST")
print("=" * 60)

small_jobs = [
    ("GAME", "game", (10_000,))
]

large_jobs = [
    ("GAME", "game", (1_000_000_000,))
]

cpu_jobs = [
    ("A", "cpu", (1, 80_000))
]

small = get_workload(small_jobs)
large = get_workload(large_jobs)
cpu = get_workload(cpu_jobs)

print("10K GAME  ->", small)
print("1B GAME   ->", large)
print("CPU       ->", cpu)

isolation = (
    small == 10_000
    and large == 1_000_000_000
    and small != large
)

print(
    "GAME WORKLOAD EXTRACTION:",
    "PASS" if isolation else "FAIL"
)

print(
    "UNKNOWN WORKLOAD SAFETY:",
    "PASS" if cpu == 0 else "FAIL"
)

print(
    "FINAL TEST:",
    "PASS"
    if isolation and cpu == 0
    else "FAIL"
)
