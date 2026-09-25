from nexus_unified_v2 import NexusUnifiedV2


def test_pattern_isolation():
    engine = NexusUnifiedV2()

    engine.memory.data.clear()

    engine.memory.record(
        (4, 0),
        "PROCESS",
        4,
        0.010,
        True,
    )

    engine.memory.record(
        (3, 5),
        "THREAD",
        1,
        0.020,
        True,
    )

    first = engine.memory.choose(
        (4, 0)
    )

    second = engine.memory.choose(
        (3, 5)
    )

    assert first is not None
    assert second is not None

    assert first.backend == "PROCESS"
    assert first.workers == 4

    assert second.backend == "THREAD"
    assert second.workers == 1

    print(
        "PATTERN ISOLATION: PASS"
    )


def test_failure_persistence():
    engine = NexusUnifiedV2()

    engine.memory.data.clear()

    engine.memory.record(
        (2, 0),
        "PROCESS",
        4,
        0.010,
        False,
    )

    entry = engine.memory.choose(
        (2, 0)
    )

    assert entry is None

    print(
        "FAILURE PERSISTENCE: PASS"
    )


def main():
    print("=" * 60)
    print("NEXUS UNIFIED INTEGRATION TEST V1")
    print("=" * 60)

    test_pattern_isolation()
    test_failure_persistence()

    print()
    print("FINAL TEST: PASS")


if __name__ == "__main__":
    main()
