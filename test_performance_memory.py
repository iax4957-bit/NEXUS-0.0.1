from nexus_performance_memory import NexusPerformanceMemory


memory = NexusPerformanceMemory("test_nexus_performance.json")

memory.record("CPU", "PROCESS", 0.327)
memory.record("CPU", "THREAD", 2.626)
memory.record("CPU", "SEQUENTIAL", 1.082)

print()
print("NEXUS PERFORMANCE MEMORY TEST")
print("History:", memory.get_history("CPU"))
print("Best backend:", memory.best_backend("CPU"))

memory2 = NexusPerformanceMemory("test_nexus_performance.json")

print()
print("AFTER RELOAD")
print("History:", memory2.get_history("CPU"))
print("Best backend:", memory2.best_backend("CPU"))

print()
if memory2.best_backend("CPU") == "PROCESS":
    print("PASS")
else:
    print("FAIL")
