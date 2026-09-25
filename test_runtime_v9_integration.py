import os
import time

from nexus_adaptive_runtime_v9 import NexusAdaptiveRuntimeV9


class TestTask:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 30


MEMORY_FILE = "test_v9_integration_memory.json"
RELIABILITY_FILE = "test_v9_integration_reliability.json"


for filename in [MEMORY_FILE, RELIABILITY_FILE]:
    if os.path.exists(filename):
        os.remove(filename)


print("=== TEST 1: BUILD HISTORY ===")

runtime1 = NexusAdaptiveRuntimeV9(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)

runtime1.reliability.history = {
    "PROCESS": {
        "successes": 1,
        "failures": 1
    },
    "THREAD": {
        "successes": 10,
        "failures": 0
    }
}

runtime1.reliability.save()

print(
    "PROCESS:",
    runtime1.reliability.get_history("PROCESS")
)

print(
    "THREAD:",
    runtime1.reliability.get_history("THREAD")
)


print("\n=== TEST 2: NEW RUNTIME ===")

runtime2 = NexusAdaptiveRuntimeV9(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)

process_confidence = runtime2._confidence_score(
    "PROCESS"
)

thread_confidence = runtime2._confidence_score(
    "THREAD"
)

print(
    "LOADED PROCESS:",
    runtime2.reliability.get_history("PROCESS")
)

print(
    "LOADED THREAD:",
    runtime2.reliability.get_history("THREAD")
)

print(
    "PROCESS CONFIDENCE:",
    process_confidence
)

print(
    "THREAD CONFIDENCE:",
    thread_confidence
)


print("\n=== TEST 3: REAL DECISION ===")

now = time.time()

history = {
    "PROCESS": {
        "average_time": 0.01,
        "runs": 5,
        "last_run": now
    },
    "THREAD": {
        "average_time": 0.10,
        "runs": 5,
        "last_run": now
    }
}

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

print(
    "SELECTED CONFIDENCE:",
    selected["confidence"]
)


print("\n=== TEST 4: REAL EXECUTION ===")

tasks = [
    TestTask(1, 1),
    TestTask(2, 2),
    TestTask(3, 3)
]

runtime3 = NexusAdaptiveRuntimeV9(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)

result = runtime3.execute(
    "CPU",
    3,
    tasks
)

print(
    "REQUESTED BACKEND:",
    result["requested_backend"]
)

print(
    "ACTUAL BACKEND:",
    result["backend"]
)

print(
    "FALLBACK:",
    result["fallback_used"]
)

print(
    "RELIABILITY:",
    result["reliability"]
)

print(
    "RELIABILITY CONFIDENCE:",
    result["reliability_confidence"]
)

print(
    "RELIABILITY SAMPLES:",
    result["reliability_samples"]
)

print(
    "RESULTS:",
    result["results"]
)


print("\n=== FINAL V9 INTEGRATION TEST ===")

persistence = (
    runtime2.reliability.get_history("PROCESS")
    == {
        "successes": 1,
        "failures": 1
    }
)

process_avoided = (
    selected["backend"] == "THREAD"
)

real_execution = (
    result["backend"] == "THREAD"
)

correct_results = (
    result["results"]
    == [(1, 30), (2, 60), (3, 90)]
)

print("PERSISTENCE:", persistence)
print("PROCESS AVOIDED:", process_avoided)
print("REAL EXECUTION:", real_execution)
print("RESULTS CORRECT:", correct_results)

print(
    "PASS:",
    persistence
    and process_avoided
    and real_execution
    and correct_results
)
