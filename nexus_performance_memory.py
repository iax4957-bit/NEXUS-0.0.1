import json
import os


class NexusPerformanceMemory:
    def __init__(self, filename="nexus_performance.json"):
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

    def record(self, task_type, backend, elapsed):
        if task_type not in self.history:
            self.history[task_type] = {}

        self.history[task_type][backend] = elapsed
        self.save()

    def best_backend(self, task_type):
        measurements = self.history.get(task_type, {})

        if not measurements:
            return None

        return min(measurements, key=measurements.get)

    def get_history(self, task_type):
        return self.history.get(task_type, {})
