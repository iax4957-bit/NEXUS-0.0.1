from nexus_adaptive_runtime_v9 import NexusAdaptiveRuntimeV9
import time

runtime = NexusAdaptiveRuntimeV9(
    workers=2,
    memory_file="test_v9_low_samples_memory.json",
    reliability_file="test_v9_low_samples_reliability.json"
)

now = time.time()

history = {
    "PROCESS": {
        "average_time": 0.01,
        "runs": 1,
        "last_run": now
    },
    "THREAD": {
        "average_time": 0.10,
        "runs": 10,
        "last_run": now
    }
}

runtime.reliability.history = {
    "PROCESS": {
        "successes": 1,
        "failures": 0
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

print("=== NEXUS V9 LOW-SAMPLE TEST ===")

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

low_sample_detected = (
    process_confidence["confidence"]
    < thread_confidence["confidence"]
)

print(
    "LOW SAMPLE DETECTED:",
    low_sample_detected
)

print("PASS:", low_sample_detected)
