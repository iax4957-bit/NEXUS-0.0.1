from nexus_adaptive_runtime_v3 import NexusAdaptiveRuntimeV3
from nexus_task_v2 import NexusTaskV2


FILE = "test_nexus_adaptive_v3.json"


def cpu_work(n):
    total = 0

    for i in range(1, n):
        total += (i * i) % 1000003

    return total


def make_tasks():
    tasks = []

    for i in range(4):
        tasks.append(
            NexusTaskV2(
                f"V3-{i + 1}",
                cpu_work,
                args=(1_000_000,),
                task_type="CPU"
            )
        )

    return tasks


runtime = NexusAdaptiveRuntimeV3(
    workers=4,
    memory_file=FILE
)


print()
print("NEXUS ADAPTIVE RUNTIME V3 TEST")

# التشغيل الأول
run1 = runtime.execute(
    "CPU",
    1_000_000,
    make_tasks()
)

print()
print("RUN 1")
print("Mode:", run1["mode"])
print("Backend:", run1["backend"])
print(f"Time: {run1['elapsed']:.3f} seconds")

# التشغيل الثاني
run2 = runtime.execute(
    "CPU",
    1_000_000,
    make_tasks()
)

print()
print("RUN 2")
print("Mode:", run2["mode"])
print("Backend:", run2["backend"])
print(f"Time: {run2['elapsed']:.3f} seconds")

history = runtime.memory.get_history(
    "CPU",
    1_000_000,
    4
)

print()
print("MEMORY:")
print(history)

correct = all(
    result == 499897499674
    for _, result in run2["results"]
)

print()

if (
    run1["mode"] == "EXPLORE"
    and run1["backend"] == "PROCESS"
    and run2["backend"] == "PROCESS"
    and correct
    and "PROCESS" in history
    and history["PROCESS"]["runs"] == 2
):
    print("PASS")
else:
    print("FAIL")
