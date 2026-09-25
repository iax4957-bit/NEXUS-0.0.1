import os

from nexus_adaptive_runtime_v7 import NexusAdaptiveRuntimeV7


RELIABILITY_FILE = "v7_reliability_test.json"
MEMORY_FILE = "v7_performance_test.json"


# تنظيف اختبارات سابقة
for filename in [
    RELIABILITY_FILE,
    MEMORY_FILE
]:
    if os.path.exists(filename):
        os.remove(filename)


print("=== RUNTIME 1 ===")

runtime1 = NexusAdaptiveRuntimeV7(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)

# تسجيل فشل PROCESS
runtime1.reliability.record_failure(
    "PROCESS",
    "intentional test failure"
)

# تسجيل نجاح THREAD
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


print("\n=== RUNTIME 2 ===")

# إنشاء Runtime جديد تمامًا
runtime2 = NexusAdaptiveRuntimeV7(
    workers=2,
    memory_file=MEMORY_FILE,
    reliability_file=RELIABILITY_FILE
)

process_reliability = (
    runtime2.reliability.reliability("PROCESS")
)

thread_reliability = (
    runtime2.reliability.reliability("THREAD")
)

print(
    "PROCESS:",
    runtime2.reliability.get_history("PROCESS")
)

print(
    "THREAD:",
    runtime2.reliability.get_history("THREAD")
)

print(
    "PROCESS RELIABILITY:",
    process_reliability
)

print(
    "THREAD RELIABILITY:",
    thread_reliability
)


print("\n=== V7 PERSISTENCE TEST ===")

passed = (
    runtime2.reliability.get_history("PROCESS")
    == {
        "successes": 0,
        "failures": 1
    }
    and
    runtime2.reliability.get_history("THREAD")
    == {
        "successes": 1,
        "failures": 0
    }
    and
    process_reliability == 0.0
    and
    thread_reliability == 1.0
)

print("PASS:", passed)
