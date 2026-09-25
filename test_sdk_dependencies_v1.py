from nexus_sdk_api_v1 import NEXUS


nexus = NEXUS(
    max_workers=2,
    exploration_repeats=1,
)

# First level
nexus.add_task(
    "A",
    "add",
    (10, 20),
)

nexus.add_task(
    "B",
    "multiply",
    (4, 5),
)

# Second level: uses A and B
nexus.add_task(
    "C",
    "add",
    (
        ("$", "A"),
        ("$", "B"),
    ),
    (
        "A",
        "B",
    ),
)

# Third level: uses C
nexus.add_task(
    "D",
    "multiply",
    (
        ("$", "C"),
        2,
    ),
    (
        "C",
    ),
)

results = nexus.run()

assert results["A"] == 30
assert results["B"] == 20
assert results["C"] == 50
assert results["D"] == 100

print("SDK DEPENDENCY TEST: PASS")
print("A =", results["A"])
print("B =", results["B"])
print("C =", results["C"])
print("D =", results["D"])
