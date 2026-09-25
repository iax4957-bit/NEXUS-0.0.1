from nexus_adaptive_runtime_v8 import NexusAdaptiveRuntimeV8


class FakeTask:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 10


runtime = NexusAdaptiveRuntimeV8(
    workers=2,
    memory_file="test_v8_memory.json",
    reliability_file="test_v8_reliability.json"
)

# PROCESS = 1 نجاح + 1 فشل = 50%
runtime.reliability.history = {
    "PROCESS": {
        "successes": 1,
        "failures": 1
    },
    "THREAD": {
        "successes": 1,
        "failures": 0
    }
}

history = {
    "PROCESS": {
        "average_time": 0.01,
        "runs": 3,
        "last_run": __import__("time").time()
    },
    "THREAD": {
        "average_time": 0.10,
        "runs": 3,
        "last_run": __import__("time").time()
    }
}

selected, learning = runtime._choose_backend(
    history,
    "CPU"
)

print("=== NEXUS V8 THRESHOLD TEST ===")
print("PROCESS RELIABILITY:",
      runtime.reliability.reliability("PROCESS"))
print("THREAD RELIABILITY:",
      runtime.reliability.reliability("THREAD"))
print("LEARNING BACKEND:",
      learning["backend"])
print("SELECTED BACKEND:",
      selected["backend"])

print("=== CHECK ===")

process_avoided = selected["backend"] != "PROCESS"

print("50% PROCESS REJECTED:", process_avoided)
print("PASS:", process_avoided)
