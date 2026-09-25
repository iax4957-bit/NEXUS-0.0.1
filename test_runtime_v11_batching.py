import tempfile

from nexus_adaptive_runtime_v11 import NexusAdaptiveRuntimeV11


class Task:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 10


class TestRuntime(NexusAdaptiveRuntimeV11):

    def __init__(self, memory_file, reliability_file):
        super().__init__(
            workers=2,
            batch_size=3,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

    def _execute_backend(self, backend, tasks):
        return [(task.task_id, task.run()) for task in tasks]


memory_file = tempfile.mktemp(
    prefix="nexus_v11_memory_",
    suffix=".json"
)

reliability_file = tempfile.mktemp(
    prefix="nexus_v11_reliability_",
    suffix=".json"
)

runtime = TestRuntime(
    memory_file,
    reliability_file
)

tasks = [
    Task(1, 1),
    Task(2, 2),
    Task(3, 3),
    Task(4, 4),
    Task(5, 5),
    Task(6, 6),
    Task(7, 7),
    Task(8, 8)
]

expected = [
    (1, 10),
    (2, 20),
    (3, 30),
    (4, 40),
    (5, 50),
    (6, 60),
    (7, 70),
    (8, 80)
]

print("=== NEXUS V11 BATCHING TEST ===")
print()

batches = runtime.create_batches(tasks)

print("BATCH SIZE:", runtime.batch_size)
print("BATCH COUNT:", len(batches))
print("BATCH SIZES:", [len(batch) for batch in batches])

batch_structure_ok = (
    len(batches) == 3
    and [len(batch) for batch in batches] == [3, 3, 2]
)

print("BATCH STRUCTURE:", batch_structure_ok)
print()

result = runtime.execute_auto_batched(
    workload_size=len(tasks),
    tasks=tasks,
    cpu_ratio=0.95,
    io_ratio=0.05
)

results_correct = result["results"] == expected
count_correct = result["task_count"] == 8
batch_count_correct = result["batch_count"] == 3

print("CLASSIFIED TYPE:", result["classified_task_type"])
print("TASK COUNT:", result["task_count"])
print("BATCH COUNT:", result["batch_count"])
print("RESULTS:", result["results"])
print()

print("RESULTS CORRECT:", results_correct)
print("TASK COUNT CORRECT:", count_correct)
print("BATCH COUNT CORRECT:", batch_count_correct)

passed = (
    batch_structure_ok
    and results_correct
    and count_correct
    and batch_count_correct
)

print()
print("FINAL PASS:", passed)
