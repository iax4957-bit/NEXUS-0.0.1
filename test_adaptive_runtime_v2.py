from nexus_adaptive_runtime_v2 import NexusAdaptiveRuntimeV2
from nexus_task_v2 import NexusTaskV2


FILE = "test_adaptive_runtime_v2.json"


def cpu_work(n):
    total = 0

    for i in range(1, n):
        total += (i * i) % 1000003

    return total


runtime = NexusAdaptiveRuntimeV2(
    workers=4,
    memory_file=FILE
)

tasks = []

for i in range(4):
    tasks.append(
        NexusTaskV2(
            f"ADAPT-{i + 1}",
            cpu_work,
            args=(1_000_000,),
            task_type="CPU"
        )
    )

backend, results, elapsed = runtime.execute(
    "CPU",
    1_000_000,
    tasks
)

print()
print("NEXUS ADAPTIVE RUNTIME V2 TEST")
print("Selected backend:", backend)
print(f"Execution time: {elapsed:.3f} seconds")

print()
for task_id, result in results:
    print(task_id, "=>", result)

history = runtime.memory.get_history(
    "CPU",
    1_000_000,
    4
)

print()
print("MEMORY V2:")
print(history)

print()

if (
    backend in ("PROCESS", "THREAD", "SEQUENTIAL")
    and elapsed > 0
    and len(results) == 4
    and all(result == 499897499674 for _, result in results)
    and backend in history
    and history[backend]["runs"] == 1
):
    print("PASS")
else:
    print("FAIL")
