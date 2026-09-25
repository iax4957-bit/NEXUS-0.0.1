import subprocess
import sys


TESTS = [
    ("MAIN SELF TESTS", ["python", "nexus_unified_v2.py"]),
    ("MEMORY PATTERN", ["python", "test_unified_memory_v1.py"]),
    ("FALLBACK PRECHECK", ["python", "test_unified_fallback_v1.py"]),
    ("FALLBACK BEHAVIOR", ["python", "test_unified_fallback_v2.py"]),
    ("UNIFIED INTEGRATION", ["python", "test_unified_integration_v1.py"]),
    ("REAL FALLBACK INTEGRATION", [
        "python",
        "test_unified_fallback_integration_v1.py",
    ]),
    ("FALLBACK MEMORY", [
        "python",
        "test_unified_fallback_memory_v1.py",
    ]),
]


def main():
    print("=" * 60)
    print("NEXUS UNIFIED V2 REGRESSION TEST V1")
    print("=" * 60)

    print()
    print("STEP 1: MAIN FILE COMPILE")

    result = subprocess.run(
        [
            "python",
            "-m",
            "py_compile",
            "nexus_unified_v2.py",
        ]
    )

    if result.returncode != 0:
        print()
        print("REGRESSION STOPPED: MAIN COMPILE FAILED")
        return 1

    print("MAIN COMPILE: PASS")

    passed = 1

    for name, command in TESTS:

        print()
        print("=" * 60)
        print(f"TEST: {name}")
        print("=" * 60)

        result = subprocess.run(command)

        if result.returncode != 0:
            print()
            print("=" * 60)
            print(f"REGRESSION FAILURE: {name}")
            print("=" * 60)
            return 1

        print()
        print(f"{name}: PASS")
        passed += 1

    print()
    print("=" * 60)
    print("NEXUS REGRESSION RESULT")
    print("=" * 60)
    print(f"PASSED TEST GROUPS: {passed}")
    print("ALL REGRESSION TESTS: PASS")
    print("CURRENT TESTING CYCLE: COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
