import time


class NexusAdaptiveLearningV2:
    def __init__(
        self,
        backends=None,
        max_age=300,
        min_runs=3
    ):
        if backends is None:
            backends = [
                "PROCESS",
                "THREAD",
                "SEQUENTIAL"
            ]

        self.backends = backends
        self.max_age = max_age
        self.min_runs = min_runs

    def _is_fresh(self, measurement):
        timestamp = measurement.get("last_run")

        if timestamp is None:
            return False

        age = time.time() - timestamp

        return age <= self.max_age

    def _score(self, measurement):
        average = measurement.get("average_time")

        if average is None:
            return float("inf")

        return average

    def choose_backend(
        self,
        history,
        task_type
    ):
        fresh = {}

        for backend, measurement in history.items():
            if self._is_fresh(measurement):
                fresh[backend] = measurement

        for backend in self.backends:
            if backend not in fresh:
                return backend

        if not fresh:
            if task_type == "CPU":
                return "PROCESS"

            if task_type == "IO":
                return "THREAD"

            return "SEQUENTIAL"

        return min(
            fresh,
            key=lambda backend:
                self._score(fresh[backend])
        )
