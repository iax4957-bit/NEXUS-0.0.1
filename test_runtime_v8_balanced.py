from nexus_adaptive_runtime_v8 import NexusAdaptiveRuntimeV8
import time

runtime = NexusAdaptiveRuntimeV8(
    workers=2,
    memory_file="test_v8_balanced_memory.json",
    reliability_file="test_v8_balanced_reliability.json"
)

now = time.time()

# PROCESS: سريع وموثوق
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

runtime.reliability.history = {
    "PROCESS": {
        "successes": 5,
        "failures": 0
    },
    "THREAD": {
        "successes": 5,
        "failures": 0
    }
}

selected, learning = runtime._choose_backend(
    history,
    "CPU"
)

print("=== NEXUS V8 BALANCED TEST ===")
print("PROCESS PERFORMANCE:", history["PROCESS"]["average_time"])
print("THREAD PERFORMANCE:", history["THREAD"]["average_time"])
print("PROCESS RELIABILITY:",
      runtime.reliability.reliability("PROCESS"))
print("THREAD RELIABILITY:",
      runtime.reliability.reliability("THREAD"))
print("LEARNING BACKEND:", learning["backend"])
print("SELECTED BACKEND:", selected["backend"])

print("=== CHECK ===")

process_selected = selected["backend"] == "PROCESS"

print("FAST RELIABLE PROCESS SELECTED:", process_selected)
print("PASS:", process_selected)
