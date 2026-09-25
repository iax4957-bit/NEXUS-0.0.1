import os

from nexus_adaptive_runtime_v7 import NexusAdaptiveRuntimeV7


RELIABILITY_FILE = "v7_decision_reliability.json"
MEMORY_FILE = "v7_decision_memory.json"


# تنظيف ملفات الاختبار
for filename in [
    RELIABILITY_FILE,
    MEMORY_FILE
]:
    if os.path.exists(filename):
        os.remove(filename)


print("=== STEP 1: CREATE BAD PROCESS HISTORY ===")

runtime1 = NexusAdaptiveRuntimeV7(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)

# PROCESS فشل سابقًا
runtime1.reliability.record_failure(
    "PROCESS",
    "intentional failure"
)

# THREAD نجح سابقًا
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

history = runtime2.memory.get_history(
    "CPU",
    10,
    2
)

selected, learning = runtime2._choose_backend(
    history,
    "CPU"
)

print(
    "SELECTED BACKEND:",
    selected["backend"]
)

print(
    "PROCESS RELIABILITY:",
    runtime2.reliability.reliability(
        "PROCESS"
    )
)

print(
    "THREAD RELIABILITY:",
    runtime2.reliability.reliability(
        "THREAD"
    )
)


print("\n=== DECISION TEST ===")

passed = (
    selected["backend"] != "PROCESS"
    and
    runtime2.reliability.reliability(
        "PROCESS"
    ) == 0.0
)

print("PROCESS AVOIDED:", selected["backend"] != "PROCESS")
print("PASS:", passed)

