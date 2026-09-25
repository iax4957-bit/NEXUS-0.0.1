from nexus_task_classifier_v1 import NexusTaskClassifierV1


classifier = NexusTaskClassifierV1()


tests = [
    {
        "name": "CPU TASK",
        "workload_size": 1000,
        "cpu_ratio": 0.95,
        "io_ratio": 0.05,
        "expected": "CPU"
    },

    {
        "name": "IO TASK",
        "workload_size": 1000,
        "cpu_ratio": 0.05,
        "io_ratio": 0.95,
        "expected": "IO"
    },

    {
        "name": "SMALL TASK",
        "workload_size": 5,
        "cpu_ratio": 0.50,
        "io_ratio": 0.50,
        "expected": "SMALL"
    },

    {
        "name": "MIXED TASK",
        "workload_size": 1000,
        "cpu_ratio": 0.50,
        "io_ratio": 0.50,
        "expected": "MIXED"
    }
]


print("=== NEXUS TASK CLASSIFIER V1 ===")
print()


passed = True


for test in tests:

    result = classifier.classify(
        workload_size=test["workload_size"],
        cpu_ratio=test["cpu_ratio"],
        io_ratio=test["io_ratio"]
    )

    correct = (
        result["task_type"]
        == test["expected"]
    )

    passed = passed and correct

    print(
        test["name"],
        "->",
        result["task_type"],
        "| EXPECTED:",
        test["expected"],
        "| PASS:",
        correct
    )


print()
print("FINAL PASS:", passed)
