from nexus_task_v2 import NexusTaskV2
from nexus_runtime_v3 import NexusRuntimeV3


def cpu_work(n):
    total = 0

    for i in range(1, n):
        total += (i * i) % 1000003

    return total


def io_work(value):
    return value * 2


def simple_work(a, b):
    return a + b


def main():
    tasks = [
        NexusTaskV2(
            "CPU-1",
            cpu_work,
            args=(1_000_000,),
            task_type="CPU"
        ),
        NexusTaskV2(
            "CPU-2",
            cpu_work,
            args=(1_000_000,),
            task_type="CPU"
        ),
        NexusTaskV2(
            "IO-1",
            io_work,
            args=(50,),
            task_type="IO"
        ),
        NexusTaskV2(
            "SIMPLE-1",
            simple_work,
            args=(10, 20),
            task_type="SIMPLE"
        ),
    ]

    runtime = NexusRuntimeV3(workers=4)

    print("NEXUS RUNTIME V3 TEST")

    results = runtime.execute(tasks)

    for task_id, result in results:
        print(task_id, "=>", result)

    expected_cpu = cpu_work(1_000_000)

    correct = (
        dict(results)["CPU-1"] == expected_cpu
        and dict(results)["CPU-2"] == expected_cpu
        and dict(results)["IO-1"] == 100
        and dict(results)["SIMPLE-1"] == 30
    )

    print("All results correct:", correct)


if __name__ == "__main__":
    main()
