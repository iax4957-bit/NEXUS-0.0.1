import time


class NexusAdaptiveLearningV3:
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

        return (
            time.time() - timestamp
        ) <= self.max_age

    def _confidence(self, measurement):
        runs = measurement.get("runs", 0)

        if runs <= 0:
            return 0.0

        return min(
            runs / self.min_runs,
            1.0
        )

    def _needs_exploration(self, history):
        for backend in self.backends:
            if backend not in history:
                return True, backend

            measurement = history[backend]

            if not self._is_fresh(measurement):
                return True, backend

            if measurement.get("runs", 0) < self.min_runs:
                return True, backend

        return False, None

    def decide(self, history, task_type):
        needs_exploration, backend = (
            self._needs_exploration(history)
        )

        if needs_exploration:
            return {
                "mode": "EXPLORE",
                "backend": backend,
                "reason": "insufficient_or_old_data"
            }

        if not history:
            if task_type == "CPU":
                backend = "PROCESS"
            elif task_type == "IO":
                backend = "THREAD"
            else:
                backend = "SEQUENTIAL"

            return {
                "mode": "EXPLORE",
                "backend": backend,
                "reason": "no_history"
            }

        fresh = {
            name: measurement
            for name, measurement in history.items()
            if self._is_fresh(measurement)
        }

        if not fresh:
            return {
                "mode": "EXPLORE",
                "backend": self.backends[0],
                "reason": "all_data_expired"
            }

        best = min(
            fresh,
            key=lambda name:
                fresh[name].get(
                    "average_time",
                    float("inf")
                )
        )

        return {
            "mode": "EXPLOIT",
            "backend": best,
            "reason": "best_recent_average",
            "confidence": self._confidence(
                fresh[best]
            )
        }
