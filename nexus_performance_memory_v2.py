import json
import os


class NexusPerformanceMemoryV2:
    def __init__(self, filename="nexus_performance_v2.json"):
        self.filename = filename
        self.history = {}
        self.load()

    def load(self):
        if not os.path.exists(self.filename):
            self.history = {}
            return

        try:
            with open(self.filename, "r") as file:
                self.history = json.load(file)
        except (json.JSONDecodeError, OSError):
            self.history = {}

    def save(self):
        with open(self.filename, "w") as file:
            json.dump(self.history, file, indent=4)

    def record(
        self,
        task_type,
        workload_size,
        workers,
        backend,
        elapsed
    ):
        task_type = str(task_type)
        workload_size = str(workload_size)
        workers = str(workers)

        self.history.setdefault(task_type, {})
        self.history[task_type].setdefault(workload_size, {})
        self.history[task_type][workload_size].setdefault(
            workers,
            {}
        )

        current = self.history[task_type][workload_size][workers]

        if backend not in current:
            current[backend] = {
                "best_time": elapsed,
                "runs": 1
            }
        else:
            current[backend]["best_time"] = min(
                current[backend]["best_time"],
                elapsed
            )
            current[backend]["runs"] += 1

        self.save()

    def get_history(
        self,
        task_type,
        workload_size,
        workers
    ):
        return (
            self.history
            .get(str(task_type), {})
            .get(str(workload_size), {})
            .get(str(workers), {})
        )

    def best_backend(
        self,
        task_type,
        workload_size,
        workers
    ):
        measurements = self.get_history(
            task_type,
            workload_size,
            workers
        )

        if not measurements:
            return None

        return min(
            measurements,
            key=lambda backend:
                measurements[backend]["best_time"]
        )
