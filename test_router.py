from nexus_router import NexusRouter
from nexus_task_v2 import NexusTaskV2


def dummy():
    return 1


def main():
    tasks = [
        NexusTaskV2("CPU-1", dummy, task_type="CPU"),
        NexusTaskV2("IO-1", dummy, task_type="IO"),
        NexusTaskV2("SIMPLE-1", dummy, task_type="SIMPLE"),
        NexusTaskV2("CPU-2", dummy, task_type="CPU"),
    ]

    router = NexusRouter()
    groups = router.group_tasks(tasks)

    print("NEXUS ROUTER TEST")

    for backend, backend_tasks in groups.items():
        print(
            backend,
            "=>",
            [task.task_id for task in backend_tasks]
        )


if __name__ == "__main__":
    main()
