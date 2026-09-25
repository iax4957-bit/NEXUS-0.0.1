from nexus_performance_memory_v2 import NexusPerformanceMemoryV2


FILE = "test_nexus_performance_v2.json"

memory = NexusPerformanceMemoryV2(FILE)

memory.record("CPU", 1_000_000, 4, "PROCESS", 0.327)
memory.record("CPU", 1_000_000, 4, "PROCESS", 0.350)
memory.record("CPU", 1_000_000, 4, "THREAD", 2.626)
memory.record("CPU", 1_000_000, 4, "SEQUENTIAL", 1.082)

print()
print("NEXUS PERFORMANCE MEMORY V2 TEST")

history = memory.get_history("CPU", 1_000_000, 4)

print("History:")
print(history)

print()
print("Best backend:", memory.best_backend("CPU", 1_000_000, 4))

memory2 = NexusPerformanceMemoryV2(FILE)

print()
print("AFTER RELOAD")
print(memory2.get_history("CPU", 1_000_000, 4))
print("Best backend:", memory2.best_backend("CPU", 1_000_000, 4))

print()
process_runs = (
    memory2
    .get_history("CPU", 1_000_000, 4)
    ["PROCESS"]["runs"]
)

best_time = (
    memory2
    .get_history("CPU", 1_000_000, 4)
    ["PROCESS"]["best_time"]
)

if (
    memory2.best_backend("CPU", 1_000_000, 4) == "PROCESS"
    and process_runs == 2
    and best_time == 0.327
):
    print("PASS")
else:
    print("FAIL")
