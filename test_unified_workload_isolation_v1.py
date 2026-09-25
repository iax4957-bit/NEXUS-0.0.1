import os
import tempfile

from nexus_unified_v2 import LearningMemory


with tempfile.TemporaryDirectory() as tmp:
    memory_file = os.path.join(
        tmp,
        "memory.json",
    )

    memory = LearningMemory(
        filename=memory_file
    )

    pattern = (1, 0)

    # 10K -> THREAD x1 is fastest
    memory.record(
        pattern,
        10_000,
        "THREAD",
        1,
        0.010,
        True,
    )

    memory.record(
        pattern,
        10_000,
        "PROCESS",
        1,
        0.100,
        True,
    )

    # 1B -> PROCESS x1 is fastest
    memory.record(
        pattern,
        1_000_000_000,
        "THREAD",
        1,
        1.000,
        True,
    )

    memory.record(
        pattern,
        1_000_000_000,
        "PROCESS",
        1,
        0.020,
        True,
    )

    choice_10k = memory.choose(
        pattern,
        10_000,
    )

    choice_1b = memory.choose(
        pattern,
        1_000_000_000,
    )

    print("10K   ->", choice_10k.backend, "x", choice_10k.workers)
    print("1B    ->", choice_1b.backend, "x", choice_1b.workers)

    assert choice_10k.backend == "THREAD"
    assert choice_1b.backend == "PROCESS"

    print("WORKLOAD ISOLATION: PASS")
    print("CROSS-WORKLOAD ISOLATION: PASS")
    print("FINAL TEST: PASS")
