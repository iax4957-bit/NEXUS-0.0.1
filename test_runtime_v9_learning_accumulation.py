import os
import tempfile

from nexus_adaptive_runtime_v9 import NexusAdaptiveRuntimeV9


class Task:

    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 10


class ControlledRuntime(NexusAdaptiveRuntimeV9):

    def __init__(self, memory_file, reliability_file):
        super().__init__(
            workers=2,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

        self.execution_count = {
            "PROCESS": 0,
            "THREAD": 0,
            "SEQUENTIAL": 0
        }

    def _execute_backend(self, backend, tasks):

        self.execution_count[backend] += 1

        return [
            (task.task_id, task.run())
            for task in tasks
        ]


memory_file = tempfile.mktemp(
    prefix="nexus_acc_memory_",
    suffix=".json"
)

reliability_file = tempfile.mktemp(
    prefix="nexus_acc_reliability_",
    suffix=".json"
)


runtime = ControlledRuntime(
    memory_file,
    reliability_file
)


tasks = [
    Task(1, 3),
    Task(2, 6),
    Task(3, 9)
]


print("=== NEXUS V9 LEARNING ACCUMULATION ===")
print()


expected = [
    (1, 30),
    (2, 60),
    (3, 90)
]


all_correct = True


for run in range(1, 11):

    result = runtime.execute(
        "CPU",
        3,
        tasks
    )

    correct = (
        result["results"] == expected
    )

    all_correct = (
        all_correct and correct
    )

    print(
        f"RUN {run:02d} | "
        f"BACKEND={result['backend']} | "
        f"RESULTS_CORRECT={correct}"
    )


print()
print("=== ACCUMULATED PERFORMANCE MEMORY ===")

history = runtime.memory.get_history(
    "CPU",
    3,
    2
)

for backend, data in history.items():

    print(
        backend,
        "| runs =", data["runs"],
        "| average_time =", data["average_time"],
        "| best_time =", data["best_time"]
    )


print()
print("=== ACCUMULATED RELIABILITY ===")

for backend in [
    "PROCESS",
    "THREAD",
    "SEQUENTIAL"
]:

    reliability_history = (
        runtime.reliability.get_history(
            backend
        )
    )

    confidence = (
        runtime._confidence_score(
            backend
        )
    )

    print(
        backend,
        "|",
        reliability_history,
        "| confidence =",
        confidence["confidence"],
        "| samples =",
        confidence["samples"]
    )


print()
print("=== VALIDATION ===")


total_runs = sum(
    data["runs"]
    for data in history.values()
)


performance_accumulated = (
    total_runs == 10
)


reliability_accumulated = all(
    runtime.reliability.get_history(
        backend
    )["successes"]
    +
    runtime.reliability.get_history(
        backend
    )["failures"]
    > 0
    for backend in history
)


memory_persisted = os.path.exists(
    memory_file
)

reliability_persisted = os.path.exists(
    reliability_file
)


print(
    "TOTAL PERFORMANCE RUNS:",
    total_runs
)

print(
    "PERFORMANCE ACCUMULATED:",
    performance_accumulated
)

print(
    "RELIABILITY ACCUMULATED:",
    reliability_accumulated
)

print(
    "MEMORY PERSISTED:",
    memory_persisted
)

print(
    "RELIABILITY PERSISTED:",
    reliability_persisted
)

print(
    "ALL RESULTS CORRECT:",
    all_correct
)


passed = (
    performance_accumulated
    and reliability_accumulated
    and memory_persisted
    and reliability_persisted
    and all_correct
)


print()
print("PASS:", passed)
