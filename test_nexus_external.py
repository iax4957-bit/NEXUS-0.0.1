from nexus_unified_v2 import NexusUnifiedV2

nexus = NexusUnifiedV2()

nexus.add_task(
    "A",
    "add",
    args=(100, 200),
)

nexus.add_task(
    "B",
    "multiply",
    args=(20, 5),
)

results = nexus.run()

print("NEXUS EXTERNAL TEST")
print("RESULTS:", results)
print("STATUS:", "PASS" if results["A"] == 300 and results["B"] == 100 else "FAIL")
