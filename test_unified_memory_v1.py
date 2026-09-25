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

with tempfile.TemporaryDirectory() as tmp:
    memory_file = os.path.join(
        tmp,
        "memory.json",
    )

    memory = LearningMemory(
        filename=memory_file
    )

    # Pattern A: PROCESS x4 is fast
    memory.record(
        (4, 0),
        100,
        "PROCESS",
        4,
        0.010,
        True,
    )

    # Pattern B: THREAD x1 is fast
    memory.record(
        (3, 5),
        100,
        "THREAD",
        1,
        0.020,
        True,
    )

    # Make PROCESS x4 artificially very slow
    memory.record(
        (3, 5),
        100,
        "PROCESS",
        4,
        1.000,
        True,
    )

    choice_a = memory.choose(
        (4, 0),
        100,
    )

    choice_b = memory.choose(
        (3, 5),
        100,
    )

    assert choice_a is not None
    assert choice_b is not None

    assert choice_a.backend == "PROCESS"
    assert choice_a.workers == 4

    assert choice_b.backend == "THREAD"
    assert choice_b.workers == 1

print("============================================================")
print("NEXUS LEARNING MEMORY PATTERN TEST")
print("============================================================")
print("PATTERN (4,0): PROCESS x4")
print("PATTERN (3,5): THREAD x1")
print("PATTERN ISOLATION: PASS")
print("NO CROSS-PATTERN LEARNING: PASS")
print("FINAL TEST: PASS")
