import json
import os


class WorkloadAwareMemoryV1:
    def __init__(self):
        self.data = {}

    def make_key(self, pattern, workload, backend, workers):
        return (
            f"{pattern[0]}:"
            f"{pattern[1]}:"
            f"{workload}:"
            f"{backend}:"
            f"{workers}"
        )

    def record(self, pattern, workload, backend, workers):
        key = self.make_key(
            pattern,
            workload,
            backend,
            workers,
        )
        self.data[key] = {
            "pattern": pattern,
            "workload": workload,
            "backend": backend,
            "workers": workers,
        }

    def choose(self, pattern, workload):
        matches = []

        for entry in self.data.values():
            if entry["pattern"] == pattern and entry["workload"] == workload:
                matches.append(entry)

        if not matches:
            return None

        return matches[0]


print("=" * 60)
print("NEXUS WORKLOAD-AWARE MEMORY V1 TEST")
print("=" * 60)

memory = WorkloadAwareMemoryV1()

pattern = (1, 0)

memory.record(pattern, 10_000, "THREAD", 1)
memory.record(pattern, 10_000_000, "PROCESS", 1)
memory.record(pattern, 1_000_000_000, "THREAD", 2)

small = memory.choose(pattern, 10_000)
medium = memory.choose(pattern, 10_000_000)
large = memory.choose(pattern, 1_000_000_000)

print("10K   ->", small["backend"], "x", small["workers"])
print("10M   ->", medium["backend"], "x", medium["workers"])
print("1B    ->", large["backend"], "x", large["workers"])

is_isolated = (
    small["backend"] == "THREAD"
    and medium["backend"] == "PROCESS"
    and large["backend"] == "THREAD"
    and small["workload"] != medium["workload"]
    and medium["workload"] != large["workload"]
)

print("WORKLOAD ISOLATION:", "PASS" if is_isolated else "FAIL")
cross_isolation = (
    small["workload"] == 10_000
    and large["workload"] == 1_000_000_000
    and small["workload"] != large["workload"]
)

print("CROSS-WORKLOAD ISOLATION:", "PASS" if cross_isolation else "FAIL")

print("FINAL TEST:", "PASS" if is_isolated else "FAIL")
