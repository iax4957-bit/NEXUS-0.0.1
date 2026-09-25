from nexus_adaptive_learning import NexusAdaptiveLearning


learning = NexusAdaptiveLearning()

print()
print("NEXUS ADAPTIVE LEARNING TEST")

# الحالة 1: لا توجد معرفة
backend_1 = learning.choose_backend({}, "CPU")
print("Empty history =>", backend_1)

# الحالة 2: معرفة PROCESS فقط
history_2 = {
    "PROCESS": {
        "best_time": 0.311,
        "runs": 1
    }
}

backend_2 = learning.choose_backend(
    history_2,
    "CPU"
)

print("PROCESS known =>", backend_2)

# الحالة 3: كل Backends معروفة
history_3 = {
    "PROCESS": {
        "best_time": 0.311,
        "runs": 3
    },
    "THREAD": {
        "best_time": 2.500,
        "runs": 3
    },
    "SEQUENTIAL": {
        "best_time": 1.100,
        "runs": 3
    }
}

backend_3 = learning.choose_backend(
    history_3,
    "CPU"
)

print("All known =>", backend_3)

print()

if (
    backend_1 == "PROCESS"
    and backend_2 in ("THREAD", "SEQUENTIAL")
    and backend_3 == "PROCESS"
):
    print("PASS")
else:
    print("FAIL")
