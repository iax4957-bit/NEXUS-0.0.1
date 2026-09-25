from nexus_adaptive_runner import NexusAdaptiveRunner
from nexus_task_v2 import NexusTaskV2


def cpu_work(n):
    total = 0

    for i in range(1, n):
        total += (i * i) % 1000003

    return total


def make_tasks():
    return [
        NexusTaskV2(
            f"CPU-{i}",
            cpu_work,
            args=(1_000_000,),
            task_type="CPU"
        )
        for i in range(1, 5)
    ]


def main():
    runner = NexusAdaptiveRunner(workers=4)

    print("NEXUS ADAPTIVE RUNNER TEST")
    print()

    results_process, process_time = runner.run_backend(
        "CPU",
        "PROCESS",
        make_tasks()
    )

    results_thread, thread_time = runner.run_backend(
        "CPU",
        "THREAD",
        make_tasks()
    )

    results_sequential, sequential_time = runner.run_backend(
        "CPU",
        "SEQUENTIAL",
        make_tasks()
    )

    expected = cpu_work(1_000_000)

    print(f"PROCESS:    {process_time:.3f} seconds")
    print(f"THREAD:     {thread_time:.3f} seconds")
    print(f"SEQUENTIAL: {sequential_time:.3f} seconds")
    print()

    print("Results correct:",
          all(result == expected for _, result in results_process)
          and all(result == expected for _, result in results_thread)
          and all(result == expected for _, result in results_sequential))

    print()
    print("Performance history:")
    print(runner.adaptive.get_history("CPU"))

    print()
    print("Best backend:",
          runner.adaptive.best_backend("CPU"))


if __name__ == "__main__":
    main()
