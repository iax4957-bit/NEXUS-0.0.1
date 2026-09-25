import nexus_unified_v2 as nexus

MEMORY_FILE = "nexus_same_pattern_memory_v1.json"


def physics_workload(value):
    total = 0.0
    for i in range(value):
        x = float(i % 1000)
        y = float((i * 3) % 1000)
        total += (x * x + y * y) ** 0.5
    return total


def ai_workload(value):
    total = 0
    for i in range(value):
        x = (i * 17 + 11) % 100003
        total += x
    return total


nexus.FUNCTIONS["physics"] = physics_workload
nexus.FUNCTIONS["ai"] = ai_workload


def run_test(name, operation):
    runtime = nexus.NexusUnifiedV2(
        max_workers=4,
        exploration_repeats=1,
    )

    runtime.memory = nexus.LearningMemory(MEMORY_FILE)

    runtime.add_task(
        f"{name}_1",
        operation,
        args=(500000,),
    )

    runtime.add_task(
        f"{name}_2",
        operation,
        args=(500000,),
    )

    print(f"\n{name}")
    print("-" * 40)

    runtime.run()


print("=" * 60)
print("NEXUS SAME PATTERN TEST V1")
print("=" * 60)

print("\nPHASE 1: PHYSICS")
run_test("PHYSICS", "physics")

print("\nPHASE 2: AI")
run_test("AI", "ai")

print("\nPHASE 3: PHYSICS AGAIN")
run_test("PHYSICS AGAIN", "physics")

print("\nPHASE 4: AI AGAIN")
run_test("AI AGAIN", "ai")

print("\nSAME PATTERN TEST COMPLETE")
