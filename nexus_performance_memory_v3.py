import json
import os
import time


class NexusPerformanceMemoryV3:
    def __init__(self, filename="nexus_performance_v3.json"):
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
        backend = str(backend)

        self.history.setdefault(task_type, {})
        self.history[task_type].setdefault(workload_size, {})
        self.history[task_type][workload_size].setdefault(
            workers, {}
        )

        current = self.history[task_type][workload_size][workers]

        if backend not in current:
            current[backend] = {
                "best_time": elapsed,
                "average_time": elapsed,
                "runs": 1,
                "last_run": time.time()
            }
        else:
            measurement = current[backend]

            old_runs = measurement.get("runs", 0)
            old_average = measurement.get(
                "average_time",
                measurement.get("best_time", elapsed)
            )

            new_runs = old_runs + 1

            new_average = (
                (old_average * old_runs) + elapsed
            ) / new_runs

            measurement["best_time"] = min(
                measurement.get("best_time", elapsed),
                elapsed
            )

            measurement["average_time"] = new_average
            measurement["runs"] = new_runs
            measurement["last_run"] = time.time()

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

        valid = {
            backend: data
            for backend, data in measurements.items()
            if "average_time" in data
        }

        if not valid:
            return None

        return min(
            valid,
            key=lambda backend:
                valid[backend]["average_time"]
        )
