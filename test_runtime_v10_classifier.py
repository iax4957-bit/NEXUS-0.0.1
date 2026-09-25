import tempfile

from nexus_adaptive_runtime_v10 import NexusAdaptiveRuntimeV10


class Task:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 10


class TestRuntime(NexusAdaptiveRuntimeV10):

    def __init__(self, memory_file, reliability_file):
        super().__init__(
            workers=2,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

    def _execute_backend(self, backend, tasks):
        return [(task.task_id, task.run()) for task in tasks]


memory_file = tempfile.mktemp(
    prefix="nexus_v10_memory_",
    suffix=".json"
)

reliability_file = tempfile.mktemp(
    prefix="nexus_v10_reliability_",
    suffix=".json"
)

runtime = TestRuntime(
    memory_file,
    reliability_file
)

tasks = [
    Task(1, 3),
    Task(2, 6),
    Task(3, 9)
]

expected = [
    (1, 30),
    (2, 60),
    (3, 90)
]

tests = [
    {
        "name": "CPU",
        "workload_size": 1000,
        "cpu_ratio": 0.95,
        "io_ratio": 0.05,
        "expected_type": "CPU"
    },
    {
        "name": "IO",
        "workload_size": 1000,
        "cpu_ratio": 0.05,
        "io_ratio": 0.95,
        "expected_type": "IO"
    },
    {
        "name": "SMALL",
        "workload_size": 5,
        "cpu_ratio": 0.50,
        "io_ratio": 0.50,
        "expected_type": "SMALL"
    },
    {
        "name": "MIXED",
        "workload_size": 1000,
        "cpu_ratio": 0.50,
        "io_ratio": 0.50,
        "expected_type": "MIXED"
    }
]

print("=== NEXUS V10 CLASSIFIER INTEGRATION ===")
print()

passed = True

for test in tests:
    result = runtime.execute_auto(
        workload_size=test["workload_size"],
        tasks=tasks,
        cpu_ratio=test["cpu_ratio"],
        io_ratio=test["io_ratio"]
    )

    classified = (
        result["classified_task_type"]
        == test["expected_type"]
    )

    correct_results = (
        result["results"] == expected
    )

    test_passed = classified and correct_results
    passed = passed and test_passed

    print(
        test["name"],
        "->",
        result["classified_task_type"],
        "| BACKEND:",
        result["backend"],
        "| CLASSIFIED:",
        classified,
        "| RESULTS:",
        correct_results,
        "| PASS:",
        test_passed
    )

print()
print("CLASSIFIER INTEGRATION:", passed)
print("ALL RESULTS CORRECT:", passed)
print()
print("FINAL PASS:", passed)
