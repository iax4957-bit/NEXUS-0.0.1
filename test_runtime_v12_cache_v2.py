import tempfile

from nexus_adaptive_runtime_v12 import NexusAdaptiveRuntimeV12


class Task:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 10


class TestRuntime(NexusAdaptiveRuntimeV12):

    def __init__(self, memory_file, reliability_file):
        super().__init__(
            workers=2,
            batch_size=3,
            memory_file=memory_file,
            reliability_file=reliability_file
        )
        self.execution_count = 0

    def _execute_backend(self, backend, tasks):
        self.execution_count += 1
        return [(task.task_id, task.run()) for task in tasks]


memory_file = tempfile.mktemp(
    prefix="nexus_v12_memory_",
    suffix=".json"
)

reliability_file = tempfile.mktemp(
    prefix="nexus_v12_reliability_",
    suffix=".json"
)

runtime = TestRuntime(
    memory_file,
    reliability_file
)

tasks = [
    Task(1, 5),
    Task(2, 10),
    Task(3, 15),
    Task(4, 20)
]

expected = [
    (1, 50),
    (2, 100),
    (3, 150),
    (4, 200)
]

print("=== NEXUS V12 CACHE V2 TEST ===")
print()

result_1 = runtime.execute_auto_batched_cached(
    workload_size=4,
    tasks=tasks,
    cpu_ratio=0.95,
    io_ratio=0.05
)

print("RUN 1 CACHE HIT:", result_1["cache_hit"])
print("RUN 1 RESULTS CORRECT:", result_1["results"] == expected)
print("EXECUTIONS AFTER RUN 1:", runtime.execution_count)

result_2 = runtime.execute_auto_batched_cached(
    workload_size=4,
    tasks=tasks,
    cpu_ratio=0.95,
    io_ratio=0.05
)

print()
print("RUN 2 CACHE HIT:", result_2["cache_hit"])
print("RUN 2 RESULTS CORRECT:", result_2["results"] == expected)
print("EXECUTIONS AFTER RUN 2:", runtime.execution_count)

different_tasks = [
    Task(1, 6),
    Task(2, 10),
    Task(3, 15),
    Task(4, 20)
]

result_3 = runtime.execute_auto_batched_cached(
    workload_size=4,
    tasks=different_tasks,
    cpu_ratio=0.95,
    io_ratio=0.05
)

expected_3 = [
    (1, 60),
    (2, 100),
    (3, 150),
    (4, 200)
]

print()
print("RUN 3 DIFFERENT INPUT CACHE HIT:", result_3["cache_hit"])
print("RUN 3 RESULTS CORRECT:", result_3["results"] == expected_3)
print("EXECUTIONS AFTER RUN 3:", runtime.execution_count)

first_ok = (
    result_1["cache_hit"] is False
    and result_1["results"] == expected
)

second_ok = (
    result_2["cache_hit"] is True
    and result_2["results"] == expected
    and runtime.execution_count >= 2
)

third_ok = (
    result_3["cache_hit"] is False
    and result_3["results"] == expected_3
    and runtime.execution_count == 4
)

passed = first_ok and second_ok and third_ok

print()
print("FIRST RUN CACHE MISS:", first_ok)
print("SECOND RUN CACHE HIT:", second_ok)
print("DIFFERENT INPUT CACHE MISS:", third_ok)
print()
print("FINAL PASS:", passed)
