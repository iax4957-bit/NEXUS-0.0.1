from nexus_adaptive import NexusAdaptiveEngine


def main():
    engine = NexusAdaptiveEngine()

    engine.record("CPU", "PROCESS", 0.327)
    engine.record("CPU", "THREAD", 2.626)
    engine.record("CPU", "SEQUENTIAL", 1.082)

    print("NEXUS ADAPTIVE ENGINE TEST")

    print("History:")
    print(engine.get_history("CPU"))

    print()
    print("Best backend:", engine.best_backend("CPU"))

    print(
        "PASS"
        if engine.best_backend("CPU") == "PROCESS"
        else "FAIL"
    )


if __name__ == "__main__":
    main()
