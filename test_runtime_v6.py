from nexus_adaptive_runtime_v6 import NexusAdaptiveRuntimeV6


class TestTask:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * self.value


tasks = [
    TestTask(1, 2),
    TestTask(2, 3),
    TestTask(3, 4),
]


runtime = NexusAdaptiveRuntimeV6(
    workers=2,
    memory_file="v6_test_memory.json"
)

result = runtime.execute(
    task_type="CPU",
    workload_size=len(tasks),
    tasks=tasks
)

print("NEXUS V6 TEST")
print("PASS:", result["results"] == [
    (1, 4),
    (2, 9),
    (3, 16)
])

print("BACKEND:", result["backend"])
print("REQUESTED:", result["requested_backend"])
print("FALLBACK:", result["fallback_used"])
print("RELIABILITY:", result["reliability"])
print("ELAPSED:", result["elapsed"])
print("RESULTS:", result["results"])
