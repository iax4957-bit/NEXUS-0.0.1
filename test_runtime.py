from nexus_runtime import NexusRuntime


def main():
    runtime = NexusRuntime()

    tests = [
        ("CPU", "PROCESS"),
        ("IO", "THREAD"),
        ("SIMPLE", "SEQUENTIAL"),
    ]

    print("NEXUS RUNTIME TEST")

    for task_type, expected in tests:
        result = runtime.choose_backend(task_type)

        print(
            task_type,
            "=>",
            result,
            "|",
            "PASS" if result == expected else "FAIL"
        )


if __name__ == "__main__":
    main()
