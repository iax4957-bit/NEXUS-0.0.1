from nexus_task_v2 import NexusTaskV2
from nexus_runtime_v2 import NexusRuntimeV2


def cpu_work(n):
    total = 0

    for i in range(1, n):
        total += (i * i) % 1000003

    return total


def main():
    tasks = [
        NexusTaskV2("V2-1", cpu_work, args=(1_000_000,), task_type="CPU"),
        NexusTaskV2("V2-2", cpu_work, args=(1_000_000,), task_type="CPU"),
        NexusTaskV2("V2-3", cpu_work, args=(1_000_000,), task_type="CPU"),
        NexusTaskV2("V2-4", cpu_work, args=(1_000_000,), task_type="CPU"),
    ]

    runtime = NexusRuntimeV2(workers=4)

    print("NEXUS RUNTIME V2 TEST")
    print("Task type:", tasks[0].task_type)

    results = runtime.execute(tasks)

    for task_id, result in results:
        print(task_id, "=>", result)

    expected = cpu_work(1_000_000)

    print(
        "All results correct:",
        all(result == expected for _, result in results)
    )


if __name__ == "__main__":
    main()
