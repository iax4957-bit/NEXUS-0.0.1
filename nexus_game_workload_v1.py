import math
import time

def game_workload(count):
    total = 0.0

    for i in range(count):
        x = float(i)
        y = float(i % 100)
        vx = 1.5
        vy = 0.75

        x = x + vx
        y = y + vy

        distance = math.sqrt(x * x + y * y)
        total += distance

    return total


if __name__ == "__main__":
    count = 10000

    start = time.perf_counter()
    result = game_workload(count)
    elapsed = time.perf_counter() - start

    print("NEXUS GAME WORKLOAD V1")
    print("=" * 40)
    print("WORKLOAD:", count)
    print("RESULT:", result)
    print("TIME:", f"{elapsed:.6f}s")
    print("STATUS: PASS")
