import nexus_unified_v2 as nexus

MEMORY_FILE = "nexus_multi_pattern_memory_v1.json"


def game_workload(value):
    total = 0
    for i in range(value):
        total += (i * 3) % 97
    return total


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


def collision_workload(value):
    total = 0
    for i in range(value):
        x = i % 500
        y = (i * 7) % 500
        if abs(x - y) < 25:
            total += 1
    return total


nexus.FUNCTIONS["game"] = game_workload
nexus.FUNCTIONS["physics"] = physics_workload
nexus.FUNCTIONS["ai"] = ai_workload
nexus.FUNCTIONS["collision"] = collision_workload


def run_pattern(name, operation, count, task_count):
    runtime = nexus.NexusUnifiedV2(
        max_workers=4,
        exploration_repeats=1,
    )

    runtime.memory = nexus.LearningMemory(MEMORY_FILE)

    for i in range(task_count):
        runtime.add_task(
            f"{name}_{i}",
            operation,
            args=(count,),
        )

    print(f"\n{name}")
    print("-" * 40)

    runtime.run()

    print(f"PATTERN: {runtime.get_pattern(runtime.graph.tasks.values())}")
    print("COMPLETE")


print("=" * 60)
print("NEXUS MULTI-PATTERN MEMORY V1")
print("=" * 60)

print("\nPHASE 1: LEARN EACH PATTERN")

run_pattern("GAME", "game", 500000, 1)
run_pattern("PHYSICS", "physics", 500000, 2)
run_pattern("AI", "ai", 500000, 3)
run_pattern("COLLISION", "collision", 500000, 4)

print("\nPHASE 2: REVISIT IN MIXED ORDER")

run_pattern("AI AGAIN", "ai", 500000, 3)
run_pattern("GAME AGAIN", "game", 500000, 1)
run_pattern("COLLISION AGAIN", "collision", 500000, 4)
run_pattern("PHYSICS AGAIN", "physics", 500000, 2)

print("\nMULTI-PATTERN MEMORY TEST COMPLETE")
