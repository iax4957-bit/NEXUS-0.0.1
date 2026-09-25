import os
import json

from nexus_adaptive_runtime_v7 import NexusAdaptiveRuntimeV7


RELIABILITY_FILE = "v7_balanced_reliability.json"
MEMORY_FILE = "v7_balanced_memory.json"


for filename in [
    RELIABILITY_FILE,
    MEMORY_FILE
]:
    if os.path.exists(filename):
        os.remove(filename)


print("=== STEP 1: PERFORMANCE HISTORY ===")

performance_data = {
    "CPU": {
        "3": {
            "2": {
                "PROCESS": {
                    "best_time": 0.01,
                    "average_time": 0.01,
                    "runs": 10,
                    "last_run": 9999999999
                },
                "THREAD": {
                    "best_time": 0.10,
                    "average_time": 0.10,
                    "runs": 10,
                    "last_run": 9999999999
                }
            }
        }
    }
}

with open(MEMORY_FILE, "w") as file:
    json.dump(performance_data, file, indent=4)


print("PROCESS average:", 0.01)
print("THREAD average:", 0.10)


print("\n=== STEP 2: RELIABILITY HISTORY ===")

reliability_data = {
    "PROCESS": {
        "successes": 10,
        "failures": 0
    },
    "THREAD": {
        "successes": 10,
        "failures": 0
    }
}

with open(RELIABILITY_FILE, "w") as file:
    json.dump(reliability_data, file, indent=4)


print("PROCESS reliability:", 1.0)
print("THREAD reliability:", 1.0)


print("\n=== STEP 3: BACKEND DECISION ===")

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


print("\n=== BALANCED TEST ===")

passed = (
    selected["backend"] == "PROCESS"
    and selected["performance"] == 0.01
    and selected["reliability"] == 1.0
)

print(
    "FAST RELIABLE PROCESS SELECTED:",
    selected["backend"] == "PROCESS"
)

print("PASS:", passed)
