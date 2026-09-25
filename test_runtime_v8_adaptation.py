from nexus_adaptive_runtime_v8 import NexusAdaptiveRuntimeV8
import time

runtime = NexusAdaptiveRuntimeV8(
    workers=2,
    memory_file="test_v8_adaptation_memory.json",
    reliability_file="test_v8_adaptation_reliability.json"
)

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

# المرحلة 1:
# PROCESS = 2 نجاح + 3 فشل = 40%
# THREAD = 5 نجاح + 0 فشل = 100%
runtime.reliability.history = {
    "PROCESS": {
        "successes": 2,
        "failures": 3
    },
    "THREAD": {
        "successes": 5,
        "failures": 0
    }
}

selected1, learning1 = runtime._choose_backend(
    history,
    "CPU"
)

print("=== PHASE 1 ===")
print("PROCESS RELIABILITY:",
      runtime.reliability.reliability("PROCESS"))
print("THREAD RELIABILITY:",
      runtime.reliability.reliability("THREAD"))
print("LEARNING:", learning1["backend"])
print("SELECTED:", selected1["backend"])

# المرحلة 2:
# PROCESS = 6 نجاح + 3 فشل = 66.6%
runtime.reliability.history["PROCESS"] = {
    "successes": 6,
    "failures": 3
}

selected2, learning2 = runtime._choose_backend(
    history,
    "CPU"
)

print("\n=== PHASE 2 ===")
print("PROCESS RELIABILITY:",
      runtime.reliability.reliability("PROCESS"))
print("THREAD RELIABILITY:",
      runtime.reliability.reliability("THREAD"))
print("LEARNING:", learning2["backend"])
print("SELECTED:", selected2["backend"])

# التحقق
phase1_correct = selected1["backend"] == "THREAD"
phase2_correct = selected2["backend"] == "PROCESS"

print("\n=== ADAPTATION CHECK ===")
print("PHASE 1 PROCESS AVOIDED:", phase1_correct)
print("PHASE 2 PROCESS RECOVERED:", phase2_correct)
print("PASS:", phase1_correct and phase2_correct)
