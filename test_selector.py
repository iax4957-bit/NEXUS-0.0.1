from nexus_selector import NexusBackendSelector


def main():
    selector = NexusBackendSelector()

    tests = [
        ("CPU", "PROCESS"),
        ("IO", "THREAD"),
        ("SIMPLE", "SEQUENTIAL"),
    ]

    print("NEXUS BACKEND SELECTOR TEST")

    for task_type, expected in tests:
        result = selector.select(task_type)

        print(
            task_type,
            "=>",
            result,
            "|",
            "PASS" if result == expected else "FAIL"
        )


if __name__ == "__main__":
    main()
