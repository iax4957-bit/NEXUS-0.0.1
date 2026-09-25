import time

from nexus_adaptive_learning_v3 import NexusAdaptiveLearningV3


learning = NexusAdaptiveLearningV3(
    max_age=300,
    min_runs=3
)

now = time.time()

print()
print("NEXUS ADAPTIVE LEARNING V3 TEST")

# 1. لا توجد بيانات
decision_1 = learning.decide({}, "CPU")
print("Empty history =>", decision_1)

# 2. بيانات ناقصة
partial_history = {
    "PROCESS": {
        "average_time": 0.31,
        "best_time": 0.30,
        "runs": 3,
        "last_run": now
    }
}

decision_2 = learning.decide(
    partial_history,
    "CPU"
)

print("Partial history =>", decision_2)

# 3. بيانات كاملة وحديثة
complete_history = {
    "PROCESS": {
        "average_time": 0.32,
        "best_time": 0.30,
        "runs": 5,
        "last_run": now
    },
    "THREAD": {
        "average_time": 2.50,
        "best_time": 2.40,
        "runs": 5,
        "last_run": now
    },
    "SEQUENTIAL": {
        "average_time": 1.10,
        "best_time": 1.05,
        "runs": 5,
        "last_run": now
    }
}

decision_3 = learning.decide(
    complete_history,
    "CPU"
)

print("Complete history =>", decision_3)

print()

if (
    decision_1["mode"] == "EXPLORE"
    and decision_2["mode"] == "EXPLORE"
    and decision_3["mode"] == "EXPLOIT"
    and decision_3["backend"] == "PROCESS"
    and decision_3["confidence"] == 1.0
):
    print("PASS")
else:
    print("FAIL")
