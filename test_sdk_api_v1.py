from nexus_sdk_api_v1 import NEXUS


nexus = NEXUS(
    max_workers=2,
    exploration_repeats=1,
)

nexus.add_task(
    "A",
    "add",
    (100, 200),
)

nexus.add_task(
    "B",
    "multiply",
    (20, 5),
)

results = nexus.run()

assert results["A"] == 300
assert results["B"] == 100

print("EXTERNAL SDK TEST: PASS")
print("A =", results["A"])
print("B =", results["B"])
