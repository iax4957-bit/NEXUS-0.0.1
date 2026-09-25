from nexus_unified_v2 import NexusUnifiedV2


class IntegrationFallbackEngine(NexusUnifiedV2):

    def __init__(self):
        super().__init__()
        self.calls = []

    def execute_candidate(self, jobs, backend, workers):
        self.calls.append((backend, workers))

        if backend == "PROCESS":
            print(
                f"FORCED PROCESS FAILURE: "
                f"{backend} x{workers}"
            )
            return {}, 0.001, False

        if backend == "THREAD":
            print(
                f"THREAD FALLBACK SUCCESS: "
                f"{backend} x{workers}"
            )

            results = {}

            for task_id, operation, args in jobs:
                if operation == "cpu":
                    results[task_id] = args[0] * args[0]
                else:
                    raise ValueError(
                        f"Unknown operation: {operation}"
                    )

            return results, 0.002, True

        raise ValueError(
            f"Unknown backend: {backend}"
        )


def main():

    print("=" * 60)
    print("NEXUS FALLBACK INTEGRATION TEST V2")
    print("=" * 60)

    engine = IntegrationFallbackEngine()

    engine.add_task(
        "A",
        "cpu",
        (100,),
    )

    engine.add_task(
        "B",
        "cpu",
        (200,),
    )

    # --------------------------------------------------------
    # First run: force exploration to create PROCESS memory.
    # We temporarily make PROCESS faster than THREAD.
    # --------------------------------------------------------

    original_execute = engine.execute_candidate

    def learning_execute(jobs, backend, workers):

        if backend == "PROCESS":
            engine.calls.append((backend, workers))

            results = {}

            for task_id, operation, args in jobs:
                results[task_id] = args[0] * args[0]

            return results, 0.001, True

        engine.calls.append((backend, workers))

        results = {}

        for task_id, operation, args in jobs:
            results[task_id] = args[0] * args[0]

        return results, 0.010, True

    engine.execute_candidate = learning_execute

    # Clear memory so the first run must explore.
    engine.memory.data.clear()

    engine.run()

    learned = engine.memory.choose((2, 0))

    print()
    print(
        "LEARNED AFTER EXPLORATION:",
        learned.backend,
        "x",
        learned.workers,
    )

    assert learned.backend == "PROCESS"
    assert learned.workers == 1

    print("PROCESS LEARNING: PASS")

    # --------------------------------------------------------
    # Second run: PROCESS is now learned, but will fail.
    # The real exploit() fallback must switch to THREAD.
    # --------------------------------------------------------

    engine.execute_candidate = original_execute

    engine.results.clear()
    engine.completed.clear()
    engine.calls.clear()

    engine.add_task(
        "C",
        "cpu",
        (100,),
    )

    engine.add_task(
        "D",
        "cpu",
        (200,),
    )

    results = engine.run()

    print()
    print("FINAL RESULTS:", results)
    print("CALLS:", engine.calls)

    process_calls = [
        call
        for call in engine.calls
        if call[0] == "PROCESS"
    ]

    thread_calls = [
        call
        for call in engine.calls
        if call[0] == "THREAD"
    ]

    assert process_calls
    assert thread_calls

    assert results["C"] == 10000
    assert results["D"] == 40000

    print()
    print("PROCESS FAILURE: PASS")
    print("THREAD RECOVERY: PASS")
    print("RESULTS CORRECT: PASS")
    print("REAL FALLBACK INTEGRATION: PASS")
    print("FINAL TEST: PASS")


if __name__ == "__main__":
    main()
