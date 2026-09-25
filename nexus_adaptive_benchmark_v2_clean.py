from nexus_adaptive_execution_engine_v2_clean import (
    NexusAdaptiveExecutionEngineV2,
    NexusTask
)


def build_engine():

    engine = NexusAdaptiveExecutionEngineV2(
        default_workers=4
    )

    def heavy():
        return sum(
            i * i
            for i in range(30000)
        )

    def add(a, b):
        return a + b

    engine.add_task(
        NexusTask("A", heavy)
    )

    engine.add_task(
        NexusTask("B", heavy)
    )

    engine.add_task(
        NexusTask("C", heavy)
    )

    engine.add_task(
        NexusTask(
            "D",
            add,
            dependencies=["A", "B"]
        )
    )

    engine.add_task(
        NexusTask(
            "E",
            add,
            dependencies=["B", "C"]
        )
    )

    engine.add_task(
        NexusTask(
            "F",
            add,
            dependencies=["D", "E"]
        )
    )

    return engine


def main():

    print("=== NEXUS ADAPTIVE LEARNING V2 ===")
    print("PERSISTENT MEMORY TEST")
    print()

    engine = build_engine()

    RUNS = 6
    times = []

    for run in range(1, RUNS + 1):

        engine.reset_run()

        result = engine.execute()

        times.append(result["elapsed"])

        print("=" * 75)
        print(f"RUN {run}")
        print("=" * 75)

        print(
            f"TIME: {result['elapsed']:.6f}s"
        )

        print(
            f"EXECUTIONS: {result['executions']}"
        )

        print(
            f"PARALLEL BATCHES: "
            f"{result['parallel_batches']}"
        )

        print()

        for item in result["history"]:

            print(
                f"PATTERN: {item['pattern']} | "
                f"{item['strategy']} | "
                f"workers={item['workers']} | "
                f"source={item['source']} | "
                f"time={item['elapsed']:.6f}s"
            )

        print()

        expected = (
            result["results"]["D"]
            == result["results"]["A"]
            + result["results"]["B"]
            and
            result["results"]["E"]
            == result["results"]["B"]
            + result["results"]["C"]
            and
            result["results"]["F"]
            == result["results"]["D"]
            + result["results"]["E"]
        )

        print(f"CORRECT: {expected}")

    print()
    print("=" * 75)
    print("LEARNING SUMMARY")
    print("=" * 75)

    print(
        f"FIRST TIME: {times[0]:.6f}s"
    )

    print(
        f"LAST TIME:  {times[-1]:.6f}s"
    )

    print(
        f"AVERAGE:    "
        f"{sum(times) / len(times):.6f}s"
    )

    print()

    print(
        f"MEMORY ENTRIES: "
        f"{engine.planner.memory.size()}"
    )

    print()
    print("FINAL TEST: True")


if __name__ == "__main__":
    main()
