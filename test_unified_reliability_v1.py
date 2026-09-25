import importlib.util
import os
import tempfile

spec = importlib.util.spec_from_file_location(
    "nexus_unified_v2",
    "nexus_unified_v2.py",
)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

LearningMemory = module.LearningMemory


def test_reliability_failure():
    with tempfile.TemporaryDirectory() as tmp:

        memory_file = os.path.join(
            tmp,
            "reliability.json",
        )

        memory = LearningMemory(
            filename=memory_file
        )

        pattern = (4, 0)

        # PROCESS x4 succeeds twice
        memory.record(
            pattern,
            "PROCESS",
            4,
            0.010,
            True,
        )

        memory.record(
            pattern,
            "PROCESS",
            4,
            0.011,
            True,
        )

        # PROCESS x4 then fails twice
        memory.record(
            pattern,
            "PROCESS",
            4,
            0.020,
            False,
        )

        memory.record(
            pattern,
            "PROCESS",
            4,
            0.020,
            False,
        )

        entry = None

        for item in memory.data.values():
            if (
                item.backend == "PROCESS"
                and item.workers == 4
            ):
                entry = item
                break

        assert entry is not None

        assert entry.successes == 2
        assert entry.failures == 2

        assert (
            abs(entry.reliability - 0.50)
            < 1e-9
        )

        print(
            "PROCESS x4 RELIABILITY:",
            entry.reliability,
        )

        print(
            "SUCCESS COUNT:",
            entry.successes,
        )

        print(
            "FAILURE COUNT:",
            entry.failures,
        )

        print(
            "RELIABILITY TEST: PASS"
        )


def test_fallback_memory():

    with tempfile.TemporaryDirectory() as tmp:

        memory_file = os.path.join(
            tmp,
            "fallback.json",
        )

        memory = LearningMemory(
            filename=memory_file
        )

        pattern = (4, 0)

        # PROCESS x4 has failures
        memory.record(
            pattern,
            "PROCESS",
            4,
            0.010,
            False,
        )

        memory.record(
            pattern,
            "PROCESS",
            4,
            0.010,
            False,
        )

        # THREAD x2 is reliable
        memory.record(
            pattern,
            "THREAD",
            2,
            0.020,
            True,
        )

        memory.record(
            pattern,
            "THREAD",
            2,
            0.020,
            True,
        )

        choice = memory.choose(
            pattern
        )

        assert choice is not None

        assert choice.backend == "THREAD"
        assert choice.workers == 2

        print(
            "FAILED PROCESS x4 REJECTED: PASS"
        )

        print(
            "THREAD x2 SELECTED: PASS"
        )

        print(
            "FALLBACK MEMORY TEST: PASS"
        )


def main():

    print(
        "============================================================"
    )

    print(
        "NEXUS RELIABILITY + FALLBACK TEST V1"
    )

    print(
        "============================================================"
    )

    test_reliability_failure()

    print()

    test_fallback_memory()

    print()

    print(
        "============================================================"
    )

    print(
        "FINAL TEST: PASS"
    )

    print(
        "============================================================"
    )


if __name__ == "__main__":
    main()
