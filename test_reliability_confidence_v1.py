from nexus_reliability_confidence_v1 import NexusReliabilityConfidenceV1

confidence = NexusReliabilityConfidenceV1(min_samples=10)

tests = [
    ("NO DATA", 0, 0),
    ("5 SAMPLES", 3, 2),
    ("10 SAMPLES", 8, 2),
    ("20 SAMPLES", 16, 4),
]

all_passed = True

for name, successes, failures in tests:
    result = confidence.evaluate(successes, failures)

    print(f"=== {name} ===")
    print("SUCCESS:", successes)
    print("FAILURES:", failures)
    print("RELIABILITY:", result["reliability"])
    print("SAMPLES:", result["samples"])
    print("CONFIDENCE:", result["confidence"])

    if result["samples"] != successes + failures:
        all_passed = False

    if result["samples"] == 0:
        if result["reliability"] is not None:
            all_passed = False
        if result["confidence"] != 0.0:
            all_passed = False

print("\n=== CONFIDENCE TEST ===")
print("PASS:", all_passed)
