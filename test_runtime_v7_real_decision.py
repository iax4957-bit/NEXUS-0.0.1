import os

from nexus_adaptive_runtime_v7 import NexusAdaptiveRuntimeV7


RELIABILITY_FILE = "v7_real_reliability.json"
MEMORY_FILE = "v7_real_memory.json"


for filename in [
    RELIABILITY_FILE,
    MEMORY_FILE
]:
    if os.path.exists(filename):
        os.remove(filename)


print("=== STEP 1: BUILD RELIABILITY HISTORY ===")

runtime1 = NexusAdaptiveRuntimeV7(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)

runtime1.reliability.record_failure(
    "PROCESS",
    "intentional failure"
)

runtime1.reliability.record_success(
    "THREAD"
)

print(
    "PROCESS:",
    runtime1.reliability.get_history("PROCESS")
)

print(
    "THREAD:",
    runtime1.reliability.get_history("THREAD")
)


print("\n=== STEP 2: NEW RUNTIME ===")

runtime2 = NexusAdaptiveRuntimeV7(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)


class TestTask:

    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 2


tasks = [
    TestTask(1, 5),
    TestTask(2, 10),
    TestTask(3, 15)
]


print("\n=== STEP 3: REAL EXECUTION ===")

result = runtime2.execute(
    "CPU",
    3,
    tasks
)

print("REQUESTED BACKEND:", result["requested_backend"])
print("ACTUAL BACKEND:", result["backend"])
print("FALLBACK USED:", result["fallback_used"])
print("RELIABILITY:", result["reliability"])
print("RESULTS:", result["results"])


print("\n=== REAL DECISION TEST ===")

passed = (
    result["requested_backend"] == "THREAD"
    and
    result["backend"] == "THREAD"
    and
    result["fallback_used"] is False
    and
    result["results"] == [
        (1, 10),
        (2, 20),
        (3, 30)
    ]
)

print(
    "DIRECT THREAD EXECUTION:",
    result["backend"] == "THREAD"
    and result["fallback_used"] is False
)

print("PASS:", passed)
