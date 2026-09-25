from nexus_unified_v2 import NexusUnifiedV2


def main():
    print("=" * 60)
    print("NEXUS UNIFIED FALLBACK TEST V1")
    print("=" * 60)

    engine = NexusUnifiedV2()

    engine.add_task(
        "A",
        "cpu",
        (1000000,),
    )

    engine.add_task(
        "B",
        "cpu",
        (1000000,),
    )

    tasks = list(
        engine.graph.tasks.values()
    )

    jobs = engine.build_jobs(tasks)

    print()
    print("TASKS:", len(tasks))
    print("JOBS:", len(jobs))

    results, elapsed, success = (
        engine.execute_candidate(
            jobs,
            "PROCESS",
            4,
        )
    )

    print(
        "PROCESS SUCCESS:",
        success,
    )

    print(
        "PROCESS TIME:",
        round(elapsed, 6),
    )

    print(
        "RESULTS:",
        results,
    )

    if not success:
        print(
            "PROCESS BACKEND FAILED"
        )
    else:
        print(
            "PROCESS BACKEND AVAILABLE"
        )

    print()
    print(
        "FALLBACK TEST PRECHECK: PASS"
    )


if __name__ == "__main__":
    main()
