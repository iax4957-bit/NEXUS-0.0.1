import os

from nexus_adaptive_runtime_v8 import NexusAdaptiveRuntimeV8


RELIABILITY_FILE = "v7_integration_reliability.json"
MEMORY_FILE = "v7_integration_memory.json"


for filename in [
    RELIABILITY_FILE,
    MEMORY_FILE
]:
    if os.path.exists(filename):
        os.remove(filename)


class TestTask:

    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 3


print("=== TEST 1: INITIAL RUNTIME ===")

runtime1 = NexusAdaptiveRuntimeV8(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)

tasks = [
    TestTask(1, 10),
    TestTask(2, 20),
    TestTask(3, 30)
]

result1 = runtime1.execute(
    "CPU",
    3,
    tasks
)

print("BACKEND:", result1["backend"])
print("FALLBACK:", result1["fallback_used"])
print("RESULTS:", result1["results"])


print("\n=== TEST 2: CREATE RELIABILITY FAILURE ===")

runtime1.reliability.record_failure(
    "PROCESS",
    "integration test failure"
)

print(
    "PROCESS HISTORY:",
    runtime1.reliability.get_history("PROCESS")
)


print("\n=== TEST 3: NEW RUNTIME ===")

runtime2 = NexusAdaptiveRuntimeV8(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)

print(
    "LOADED PROCESS HISTORY:",
    runtime2.reliability.get_history("PROCESS")
)

print(
    "LOADED THREAD HISTORY:",
    runtime2.reliability.get_history("THREAD")
)


print("\n=== TEST 4: NEW DECISION ===")

history = runtime2.memory.get_history(
    "CPU",
    3,
    2
)

selected, learning = runtime2._choose_backend(
    history,
    "CPU"
)

print(
    "LEARNING BACKEND:",
    learning["backend"]
)

print(
    "SELECTED BACKEND:",
    selected["backend"]
)

print(
    "SELECTED RELIABILITY:",
    selected["reliability"]
)


print("\n=== TEST 5: REAL EXECUTION ===")

result2 = runtime2.execute(
    "CPU",
    3,
    tasks
)

print(
    "REQUESTED BACKEND:",
    result2["requested_backend"]
)

print(
    "ACTUAL BACKEND:",
    result2["backend"]
)

print(
    "FALLBACK:",
    result2["fallback_used"]
)

print(
    "RESULTS:",
    result2["results"]
)


print("\n=== FINAL INTEGRATION TEST ===")

passed = (
    result1["results"]
    == [
        (1, 30),
        (2, 60),
        (3, 90)
    ]
    and
    runtime2.reliability.get_history("PROCESS")[
        "failures"
    ] >= 1
    and
    result2["backend"] != "PROCESS"
    and
    result2["fallback_used"] is False
    and
    result2["results"]
    == [
        (1, 30),
        (2, 60),
        (3, 90)
    ]
)

print(
    "PERSISTENCE:",
    runtime2.reliability.get_history("PROCESS")[
        "failures"
    ] >= 1
)

print(
    "PROCESS AVOIDED:",
    result2["backend"] != "PROCESS"
)

print(
    "NO FALLBACK:",
    result2["fallback_used"] is False
)

print("PASS:", passed)
