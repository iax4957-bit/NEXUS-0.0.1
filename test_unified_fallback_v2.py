from nexus_unified_v2 import NexusUnifiedV2


class FallbackTestEngine(NexusUnifiedV2):

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
                f"FORCED FAILURE: "
                f"{backend} x{workers}"
            )

            return (
                {},
                0.001,
                False,
            )

        print(
            f"SUCCESS: "
            f"{backend} x{workers}"
        )

        results = {}

        for (
            task_id,
            operation,
            args,
        ) in jobs:

            if operation == "cpu":
                value = args[0] * args[0]
            else:
                raise ValueError(
                    f"Unknown operation: "
                    f"{operation}"
                )

            results[task_id] = value

        return (
            results,
            0.002,
            True,
        )


def main():

    print("=" * 60)
    print("NEXUS FALLBACK BEHAVIOR TEST V2")
    print("=" * 60)

    engine = FallbackTestEngine()

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

    result = engine.run()

    print()
    print("FINAL RESULTS:", result)
    print("CALLS:", engine.calls)

    assert result["A"] == 10000
    assert result["B"] == 40000

    assert any(
        backend == "PROCESS"
        for backend, workers
        in engine.calls
    )

    assert any(
        backend == "THREAD"
        for backend, workers
        in engine.calls
    )

    print()
    print("PROCESS FAILURE DETECTED: PASS")
    print("RECOVERY PATH DETECTED: PASS")
    print("FINAL RESULTS CORRECT: PASS")
    print("FINAL TEST: PASS")


if __name__ == "__main__":
    main()
