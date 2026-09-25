from nexus_sdk_api_v1 import NEXUS


nexus = NEXUS(
    max_workers=2,
    exploration_repeats=1,
)

# First calculation
nexus.add_task(
    "A",
    "add",
    (100, 200),
)

# Second task depends on A.
# It performs exactly the same calculation,
# so the cache can be reused after A completes.
nexus.add_task(
    "B",
    "add",
    (100, 200),
    ("A",),
)

results = nexus.run()

assert results["A"] == 300
assert results["B"] == 300

assert nexus.engine.cache_hits >= 1

print("SDK CACHE TEST: PASS")
print("A =", results["A"])
print("B =", results["B"])
print("CACHE HITS =", nexus.engine.cache_hits)
print("EXECUTIONS =", nexus.engine.execution_count)
