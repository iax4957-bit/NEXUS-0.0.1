import os
import json

from nexus_adaptive_runtime_v7 import NexusAdaptiveRuntimeV7


RELIABILITY_FILE = "v7_pr_test_reliability.json"
MEMORY_FILE = "v7_pr_test_memory.json"


# تنظيف ملفات الاختبار السابقة
for filename in [
    RELIABILITY_FILE,
    MEMORY_FILE
]:
    if os.path.exists(filename):
        os.remove(filename)


print("=== STEP 1: CREATE PERFORMANCE HISTORY ===")

performance_data = {
    "CPU": {
        "3": {
            "2": {
                "PROCESS": {
                    "best_time": 0.010,
                    "average_time": 0.010,
                    "runs": 10,
                    "last_run": 9999999999
                },
                "THREAD": {
                    "best_time": 0.100,
                    "average_time": 0.100,
                    "runs": 10,
                    "last_run": 9999999999
                }
            }
        }
    }
}

with open(MEMORY_FILE, "w") as file:
    json.dump(
        performance_data,
        file,
        indent=4
    )


print("PROCESS average:", 0.010)
print("THREAD average:", 0.100)


print("\n=== STEP 2: CREATE RELIABILITY HISTORY ===")

reliability_data = {
    "PROCESS": {
        "successes": 1,
        "failures": 9
    },
    "THREAD": {
        "successes": 10,
        "failures": 0
    }
}

with open(RELIABILITY_FILE, "w") as file:
    json.dump(
        reliability_data,
        file,
        indent=4
    )


print("PROCESS reliability:", 0.1)
print("THREAD reliability:", 1.0)


print("\n=== STEP 3: NEW RUNTIME ===")

runtime = NexusAdaptiveRuntimeV7(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)


history = runtime.memory.get_history(
    "CPU",
    3,
    2
)

selected, learning = runtime._choose_backend(
    history,
    "CPU"
)


print("LEARNING BACKEND:", learning["backend"])
print("SELECTED BACKEND:", selected["backend"])
print("SELECTED PERFORMANCE:", selected["performance"])
print("SELECTED RELIABILITY:", selected["reliability"])


print("\n=== PERFORMANCE + RELIABILITY TEST ===")

passed = (
    selected["backend"] == "THREAD"
    and selected["performance"] == 0.100
    and selected["reliability"] == 1.0
)

print(
    "LOW-RELIABILITY PROCESS AVOIDED:",
    selected["backend"] != "PROCESS"
)

print("PASS:", passed)
