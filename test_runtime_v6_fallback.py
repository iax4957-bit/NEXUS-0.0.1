from nexus_adaptive_runtime_v6 import NexusAdaptiveRuntimeV6


class TestTask:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 2


class BrokenV6(NexusAdaptiveRuntimeV6):
    def _execute_backend(self, backend, tasks):
        if backend == "PROCESS":
            raise RuntimeError("INTENTIONAL PROCESS FAILURE")
        return super()._execute_backend(backend, tasks)


tasks = [
    TestTask(1, 5),
    TestTask(2, 10),
]


runtime = BrokenV6(
    workers=2,
    memory_file="v6_fallback_test_memory.json"
)

result = runtime.execute(
    task_type="CPU",
    workload_size=len(tasks),
    tasks=tasks
)

print("NEXUS V6 FALLBACK TEST")
print("PASS:", result["results"] == [
    (1, 10),
    (2, 20)
])

print("BACKEND:", result["backend"])
print("REQUESTED:", result["requested_backend"])
print("FALLBACK:", result["fallback_used"])
print("RELIABILITY:", result["reliability"])
print("RESULTS:", result["results"])
print("PROCESS HISTORY:", runtime.reliability.get_history("PROCESS"))
print("THREAD HISTORY:", runtime.reliability.get_history("THREAD"))
