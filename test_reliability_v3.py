import os

from nexus_reliability_v3 import NexusReliabilityV3


TEST_FILE = "reliability_persistence_test.json"

# تنظيف اختبار سابق
if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)


print("=== INSTANCE 1 ===")

r1 = NexusReliabilityV3(TEST_FILE)

r1.record_success("PROCESS")
r1.record_success("PROCESS")
r1.record_failure("PROCESS", "test failure")

r1.record_success("THREAD")

print("PROCESS:", r1.get_history("PROCESS"))
print("THREAD:", r1.get_history("THREAD"))


print("\n=== INSTANCE 2 ===")

# كائن جديد تمامًا
r2 = NexusReliabilityV3(TEST_FILE)

print("PROCESS:", r2.get_history("PROCESS"))
print("THREAD:", r2.get_history("THREAD"))

print("\n=== PERSISTENCE TEST ===")

expected_process = {
    "successes": 2,
    "failures": 1
}

expected_thread = {
    "successes": 1,
    "failures": 0
}

passed = (
    r2.get_history("PROCESS") == expected_process
    and r2.get_history("THREAD") == expected_thread
    and r2.reliability("PROCESS") == 2 / 3
    and r2.reliability("THREAD") == 1.0
)

print("PROCESS RELIABILITY:", r2.reliability("PROCESS"))
print("THREAD RELIABILITY:", r2.reliability("THREAD"))
print("PASS:", passed)
