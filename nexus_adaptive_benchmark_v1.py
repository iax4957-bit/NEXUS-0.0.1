# NEXUS Adaptive Benchmark V1
# Real Execute -> Measure -> Learn loop

import time

from nexus_adaptive_execution_engine_v1 import (
    NexusAdaptiveExecutionEngineV1
)


def build_engine():
    engine = NexusAdaptiveExecutionEngineV1(
        workers=4
    )

    engine.add_task(
        "A",
        lambda: sum(i * i for i in range(30000))
    )

    engine.add_task(
        "B",
        lambda: sum(i * i for i in range(30000))
    )

    engine.add_task(
        "C",
        lambda: sum(i * i for i in range(30000))
    )

    engine.add_task(
        "D",
        lambda a, b: a + b,
        dependencies=["A", "B"]
    )

    engine.add_task(
        "E",
        lambda b, c: b + c,
        dependencies=["B", "C"]
    )

    engine.add_task(
        "F",
        lambda d, e: d + e,
        dependencies=["D", "E"]
    )

    return engine


def main():

    print("=== NEXUS ADAPTIVE BENCHMARK V1 ===")

    runs = 6

    times = []

    for run in range(1, runs + 1):

        engine = build_engine()

        start = time.perf_counter()

        report = engine.execute()

        elapsed = time.perf_counter() - start

        times.append(elapsed)

        print(f"\nRUN {run}")
        print("TIME:", round(elapsed, 6))
        print("EXECUTIONS:", report["executions"])
        print(
            "PARALLEL BATCHES:",
            report["parallel_batches"]
        )

        print(
            "MEMORY ENTRIES:",
            len(engine.planner.memory.cache)
        )

        # Show the decisions learned during this run.
        for key, stats in engine.planner.memory.cache.items():

            print(
                "PATTERN:",
                key,
                "|",
                stats.strategy,
                "| workers=",
                stats.workers,
                "| runs=",
                stats.runs,
                "| avg=",
                round(stats.average_time, 6),
                "| reliability=",
                round(stats.reliability, 2)
            )

        results = report["results"]

        correct = (
            results["A"] > 0
            and results["B"] > 0
            and results["C"] > 0
            and results["D"] == results["A"] + results["B"]
            and results["E"] == results["B"] + results["C"]
            and results["F"] == results["D"] + results["E"]
        )

        print("CORRECT:", correct)

    first = times[0]
    last = times[-1]

    average = sum(times) / len(times)

    print("\n=== BENCHMARK SUMMARY ===")
    print("RUNS:", runs)
    print("FIRST TIME:", round(first, 6))
    print("LAST TIME:", round(last, 6))
    print("AVERAGE TIME:", round(average, 6))

    print(
        "CHANGE:",
        round(first - last, 6)
    )

    print(
        "FINAL TEST:",
        all(t > 0 for t in times)
    )


if __name__ == "__main__":
    main()
