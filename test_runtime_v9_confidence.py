from nexus_adaptive_runtime_v9 import NexusAdaptiveRuntimeV9
import time

runtime = NexusAdaptiveRuntimeV9(
    workers=2,
    memory_file="test_v9_confidence_memory.json",
    reliability_file="test_v9_confidence_reliability.json"
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

# PROCESS سريع، لكن لديه 60% Reliability فقط
# و5 عينات فقط => Confidence = 0.5
runtime.reliability.history = {
    "PROCESS": {
        "successes": 3,
        "failures": 2
    },
    "THREAD": {
        "successes": 10,
        "failures": 0
    }
}

selected, learning = runtime._choose_backend(
    history,
    "CPU"
)

process_confidence = runtime._confidence_score(
    "PROCESS"
)

thread_confidence = runtime._confidence_score(
    "THREAD"
)

print("=== NEXUS V9 CONFIDENCE TEST ===")
print("LEARNING BACKEND:", learning["backend"])

print("\nPROCESS")
print("RELIABILITY:",
      runtime.reliability.reliability("PROCESS"))
print("SAMPLES:",
      process_confidence["samples"])
print("CONFIDENCE:",
      process_confidence["confidence"])

print("\nTHREAD")
print("RELIABILITY:",
      runtime.reliability.reliability("THREAD"))
print("SAMPLES:",
      thread_confidence["samples"])
print("CONFIDENCE:",
      thread_confidence["confidence"])

print("\nSELECTED BACKEND:",
      selected["backend"])

print("\n=== CHECK ===")

# PROCESS عند الحد الأدنى للـ confidence،
# لذلك يجب أن يبقى مقبولًا في تصميم V9 الحالي.
process_allowed = (
    selected["backend"] == "PROCESS"
)

print("PROCESS ALLOWED:", process_allowed)
print("PASS:", process_allowed)
