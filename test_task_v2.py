from nexus_task_v2 import NexusTaskV2


def add(a, b):
    return a + b


def main():
    task = NexusTaskV2(
        "T1",
        add,
        args=(10, 20),
        task_type="CPU"
    )

    print("NEXUS TASK V2 TEST")
    print("Task ID:", task.task_id)
    print("Task Type:", task.task_type)
    print("Result:", task.run())

    print(
        "PASS"
        if task.task_type == "CPU" and task.result == 30
        else "FAIL"
    )


if __name__ == "__main__":
    main()
