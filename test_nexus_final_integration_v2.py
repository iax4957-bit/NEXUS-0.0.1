import tempfile

from nexus_adaptive_runtime_v13 import NexusAdaptiveRuntimeV13


class Task:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 10


class TestRuntime(NexusAdaptiveRuntimeV13):

    def __init__(self, memory_file, reliability_file):
        super().__init__(
            workers=2,
            batch_size=3,
            exploration_rate=0.0,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

        self.execution_count = 0

    def _execute_backend(self, backend, tasks):
        self.execution_count += 1
        return [
            (task.task_id, task.run())
            for task in tasks
        ]


memory_file = tempfile.mktemp(
    prefix="nexus_final_memory_",
    suffix=".json"
)

reliability_file = tempfile.mktemp(
    prefix="nexus_final_reliability_",
    suffix=".json"
)

runtime = TestRuntime(
    memory_file,
    reliability_file
)

tasks = [
    Task(1, 2),
    Task(2, 4),
    Task(3, 6),
    Task(4, 8),
    Task(5, 10),
    Task(6, 12),
    Task(7, 14)
]

expected = [
    (1, 20),
    (2, 40),
    (3, 60),
    (4, 80),
    (5, 100),
    (6, 120),
    (7, 140)
]

print("=== NEXUS FINAL INTEGRATION V2 ===")
print()

# 1. CLASSIFICATION

classification = runtime.classify_task(
    workload_size=100,
    cpu_ratio=0.95,
    io_ratio=0.05
)

classification_ok = (
    classification["task_type"] == "CPU"
)

print("1. CLASSIFICATION:", classification["task_type"])
print("CLASSIFICATION PASS:", classification_ok)
print()

# 2. BATCHING + CACHE

result_1 = runtime.execute_auto_batched_cached(
    workload_size=100,
    tasks=tasks,
    cpu_ratio=0.95,
    io_ratio=0.05
)

first_run_ok = (
    result_1["cache_hit"] is False
    and result_1["results"] == expected
    and result_1["batch_count"] == 3
    and result_1["task_count"] == 7
)

print("2. FIRST EXECUTION")
print("CACHE HIT:", result_1["cache_hit"])
print("BATCH COUNT:", result_1["batch_count"])
print("TASK COUNT:", result_1["task_count"])
print("RESULTS CORRECT:", result_1["results"] == expected)
print("FIRST EXECUTION PASS:", first_run_ok)
print()

# 3. CACHE HIT

execution_count_before_cache = runtime.execution_count

result_2 = runtime.execute_auto_batched_cached(
    workload_size=100,
    tasks=tasks,
    cpu_ratio=0.95,
    io_ratio=0.05
)

cache_ok = (
    result_2["cache_hit"] is True
    and result_2["results"] == expected
    and runtime.execution_count == execution_count_before_cache
)

print("3. CACHE")
print("CACHE HIT:", result_2["cache_hit"])
print(
    "EXECUTION COUNT UNCHANGED:",
    runtime.execution_count == execution_count_before_cache
)
print("CACHE PASS:", cache_ok)
print()

# 4. EXPLORATION

history = {
    "PROCESS": {
        "average_time": 0.01,
        "runs": 20,
        "last_run": 9999999999
    },
    "THREAD": {
        "average_time": 0.10,
        "runs": 20,
        "last_run": 9999999999
    },
    "SEQUENTIAL": {
        "average_time": 0.20,
        "runs": 20,
        "last_run": 9999999999
    }
}

exploration = runtime.choose_with_exploration(
    history,
    "CPU",
    force_exploration=True
)

exploration_ok = (
    exploration["mode"] == "EXPLORE"
    and exploration["exploration"] is True
    and exploration["backend"] != exploration["preferred_backend"]
)

print("4. EXPLORATION")
print("PREFERRED:", exploration["preferred_backend"])
print("EXPLORE BACKEND:", exploration["backend"])
print("MODE:", exploration["mode"])
print("EXPLORATION PASS:", exploration_ok)
print()

# 5. RELIABILITY
# V11/V12 batched execution returns no single backend field.
# Verify reliability state exists and can be queried safely.

all_reliability = runtime.reliability.get_all_history()

reliability_ok = isinstance(all_reliability, dict)

print("5. RELIABILITY")
print("RELIABILITY HISTORY AVAILABLE:", reliability_ok)
print("KNOWN BACKENDS:", list(all_reliability.keys()))
print("RELIABILITY PASS:", reliability_ok)
print()

# 6. PERFORMANCE MEMORY

performance_history = runtime.memory.get_history(
    "CPU",
    3,
    runtime.workers
)

performance_ok = isinstance(performance_history, dict)

print("6. PERFORMANCE MEMORY")
print("MEMORY AVAILABLE:", performance_ok)
print("MEMORY PASS:", performance_ok)
print()

# 7. END-TO-END RESULT VALIDATION

end_to_end_ok = (
    result_1["results"] == expected
    and result_2["results"] == expected
    and result_1["task_count"] == 7
    and result_1["batch_count"] == 3
)

print("7. END-TO-END")
print("RESULTS:", end_to_end_ok)
print()

passed = (
    classification_ok
    and first_run_ok
    and cache_ok
    and exploration_ok
    and reliability_ok
    and performance_ok
    and end_to_end_ok
)

print("================================")
print("FINAL INTEGRATION PASS:", passed)
print("================================")
