from nexus_learning_runtime import NexusLearningRuntime
from nexus_task_v2 import NexusTaskV2


def cpu_work(n):
    total = 0

    for i in range(1, n):
        total += (i * i) % 1000003

    return total


runtime = NexusLearningRuntime(
    workers=4,
    memory_file="test_nexus_performance.json"
)

tasks = []

for i in range(4):
    tasks.append(
        NexusTaskV2(
            f"LEARN-{i + 1}",
            cpu_work,
            args=(1_000_000,),
            task_type="CPU"
        )
    )

backend, results = runtime.execute("CPU", tasks)

print()
print("NEXUS LEARNING RUNTIME TEST")
print("Selected backend:", backend)

for task_id, result in results:
    print(task_id, "=>", result)

print()
if backend == "PROCESS":
    print("LEARNING: PASS")
else:
    print("LEARNING: FAIL")
