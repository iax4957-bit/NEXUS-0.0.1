from nexus_unified_v2 import NexusUnifiedV2


class FailureMemoryEngine(NexusUnifiedV2):

    def __init__(self):
        super().__init__()
        self.calls = []

    def execute_candidate(self, jobs, backend, workers):
        self.calls.append((backend, workers))

        if backend == "PROCESS":
            print(f"FORCED PROCESS FAILURE: {backend} x{workers}")
            return {}, 0.001, False

        if backend == "THREAD":
            print(f"THREAD SUCCESS: {backend} x{workers}")

            results = {}

            for task_id, operation, args in jobs:
                if operation == "cpu":
                    results[task_id] = args[0] * args[0]

            return results, 0.002, True

        return {}, 0.001, False


def main():

    print("=" * 60)
    print("NEXUS FALLBACK MEMORY TEST V1")
    print("=" * 60)

    engine = FailureMemoryEngine()

    engine.add_task("A", "cpu", (100,))
    engine.add_task("B", "cpu", (200,))

    pattern = (2, 0)

    # Force the learned strategy to PROCESS x1.
    from nexus_unified_v2 import MemoryEntry

    engine.memory.data[
        engine.memory.make_key(pattern, "PROCESS", 1)
    ] = MemoryEntry(
        backend="PROCESS",
        workers=1,
        avg_time=0.001,
        runs=10,
        successes=10,
        failures=0,
    )

    print()
    print("BEFORE RUN:")
    print(
        "LEARNED:",
        engine.memory.choose(pattern).backend,
        "x",
        engine.memory.choose(pattern).workers,
    )

    results = engine.run()

    print()
    print("RESULTS:", results)
    print("CALLS:", engine.calls)

    assert results["A"] == 10000
    assert results["B"] == 40000

    process_calls = [
        c for c in engine.calls
        if c[0] == "PROCESS"
    ]

    thread_calls = [
        c for c in engine.calls
        if c[0] == "THREAD"
    ]

    assert process_calls
    assert thread_calls

    print()
    print("FALLBACK EXECUTION: PASS")

    process_key = engine.memory.make_key(
        pattern,
        "PROCESS",
        1,
    )

    process_entry = engine.memory.data[process_key]

    print()
    print("PROCESS MEMORY AFTER FAILURE:")
    print("RUNS:", process_entry.runs)
    print("SUCCESSES:", process_entry.successes)
    print("FAILURES:", process_entry.failures)

    assert process_entry.failures >= 1
    assert process_entry.successes < process_entry.runs

    print("FAILURE PERSISTENCE: PASS")

    next_choice = engine.memory.choose(pattern)

    print()
    print(
        "NEXT LEARNED CHOICE:",
        next_choice.backend,
        "x",
        next_choice.workers,
    )

    assert not (
        next_choice.backend == "PROCESS"
        and next_choice.workers == 1
    )

    print("PROCESS AVOIDANCE: PASS")
    print("FINAL TEST: PASS")


if __name__ == "__main__":
    main()
