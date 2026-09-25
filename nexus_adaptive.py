class NexusAdaptiveEngine:
    def __init__(self):
        self.history = {}

    def record(self, task_type, backend, elapsed):
        if task_type not in self.history:
            self.history[task_type] = {}

        self.history[task_type][backend] = elapsed

    def best_backend(self, task_type):
        if task_type not in self.history:
            return None

        measurements = self.history[task_type]

        if not measurements:
            return None

        return min(
            measurements,
            key=measurements.get
        )

    def get_history(self, task_type):
        return self.history.get(task_type, {})
