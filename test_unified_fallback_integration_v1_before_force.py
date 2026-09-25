from nexus_unified_v2 import NexusUnifiedV2


class IntegrationFallbackEngine(NexusUnifiedV2):

    def __init__(self):
        super().__init__()
        self.calls = []

    def execute_candidate(
        self,
        jobs,
        backend,
        workers,
    ):
        self.calls.append(
            (backend, workers)
        )

        if backend == "PROCESS":
            print(
                f"FORCED PROCESS FAILURE: "
                f"{backend} x{workers}"
            )

            return (
                {},
                0.001,
                False,
            )

        print(
            f"THREAD FALLBACK SUCCESS: "
            f"{backend} x{workers}"
        )

        results = {}

        for (
            task_id,
            operation,
            args,
        ) in jobs:

            if operation == "cpu":
                results[task_id] = (
                    args[0] * args[0]
                )
            else:
                raise ValueError(
                    f"Unknown operation: "
                    f"{operation}"
                )

        return (
            results,
            0.002,
            True,
        )


def main():

    print("=" * 60)
    print("NEXUS FALLBACK INTEGRATION TEST V1")
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

    results = engine.run()

    print()
    print("FINAL RESULTS:", results)
    print("CALLS:", engine.calls)

    assert results["A"] == 10000
    assert results["B"] == 40000

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

    print()
    print("PROCESS FAILURE: PASS")
    print("THREAD RECOVERY: PASS")
    print("RESULTS CORRECT: PASS")
    print("INTEGRATION TEST: PASS")


if __name__ == "__main__":
    main()
