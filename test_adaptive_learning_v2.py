import time

from nexus_adaptive_learning_v2 import NexusAdaptiveLearningV2


learning = NexusAdaptiveLearningV2(
    max_age=300
)

now = time.time()

print()
print("NEXUS ADAPTIVE LEARNING V2 TEST")

# حالة 1: بيانات حديثة
fresh_history = {
    "PROCESS": {
        "average_time": 0.31,
        "runs": 5,
        "last_run": now
    },
    "THREAD": {
        "average_time": 2.50,
        "runs": 5,
        "last_run": now
    },
    "SEQUENTIAL": {
        "average_time": 1.10,
        "runs": 5,
        "last_run": now
    }
}

backend_1 = learning.choose_backend(
    fresh_history,
    "CPU"
)

print("Fresh data =>", backend_1)

# حالة 2: PROCESS قديم
old_history = {
    "PROCESS": {
        "average_time": 0.31,
        "runs": 5,
        "last_run": now - 1000
    },
    "THREAD": {
        "average_time": 2.50,
        "runs": 5,
        "last_run": now
    },
    "SEQUENTIAL": {
        "average_time": 1.10,
        "runs": 5,
        "last_run": now
    }
}

backend_2 = learning.choose_backend(
    old_history,
    "CPU"
)

print("PROCESS expired =>", backend_2)

# حالة 3: لا توجد بيانات
backend_3 = learning.choose_backend(
    {},
    "CPU"
)

print("Empty history =>", backend_3)

print()

if (
    backend_1 == "PROCESS"
    and backend_2 == "PROCESS"
    and backend_3 == "PROCESS"
):
    print("PASS")
else:
    print("FAIL")
