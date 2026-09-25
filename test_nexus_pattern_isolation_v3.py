import nexus_unified_v2
from nexus_unified_v2 import NexusUnifiedV2
from nexus_game_workload_v1 import game_workload

nexus_unified_v2.FUNCTIONS["game"] = game_workload


def physics_workload(count):
    total = 0.0

    for i in range(count):
        x = float(i % 1000)
        y = float((i * 3) % 1000)

        vx = 1.25
        vy = -0.75

        x += vx
        y += vy

        total += (x * x + y * y) ** 0.5

    return total


nexus_unified_v2.FUNCTIONS["physics"] = physics_workload


def run_game(count):
    runtime = NexusUnifiedV2(
        max_workers=4,
        exploration_repeats=1,
    )

    runtime.add_task(
        "GAME",
        "game",
        args=(count,),
    )

    return runtime.run()


def run_physics(count):
    runtime = NexusUnifiedV2(
        max_workers=4,
        exploration_repeats=1,
    )

    runtime.add_task(
        "P1",
        "physics",
        args=(count,),
    )

    runtime.add_task(
        "P2",
        "physics",
        args=(count,),
    )

    return runtime.run()


print("NEXUS PATTERN ISOLATION V3")
print("=" * 60)

COUNT = 1000000

print()
print("PHASE 1: GAME")
run_game(COUNT)

print()
print("PHASE 2: PHYSICS")
run_physics(COUNT)

print()
print("PHASE 3: GAME AGAIN")
run_game(COUNT)

print()
print("PATTERN ISOLATION V3 COMPLETE")
