import time

class NexusAdaptiveLearningV4:
    def __init__(self, backends=None, max_age=300, min_runs=3):
        self.backends = backends or ["PROCESS", "THREAD", "SEQUENTIAL"]
        self.max_age = max_age
        self.min_runs = min_runs

    def _fresh(self, m):
        t = m.get("last_run")
        return t is not None and time.time() - t <= self.max_age

    def _confidence(self, m):
        return min(m.get("runs", 0) / self.min_runs, 1.0)

    def decide(self, history, task_type):
        valid = {
            b: m for b, m in history.items()
            if self._fresh(m) and m.get("average_time") is not None
        }

        if not valid:
            default = (
                "PROCESS" if task_type == "CPU"
                else "THREAD" if task_type == "IO"
                else "SEQUENTIAL"
            )
            return {
                "mode": "EXPLORE",
                "backend": default,
                "reason": "no_valid_data",
                "confidence": 0.0
            }

        best = min(
            valid,
            key=lambda b: valid[b]["average_time"]
        )

        confidence = self._confidence(valid[best])

        if confidence < 1.0:
            return {
                "mode": "EXPLORE",
                "backend": best,
                "reason": "insufficient_confidence",
                "confidence": confidence
            }

        return {
            "mode": "EXPLOIT",
            "backend": best,
            "reason": "best_recent_average",
            "confidence": confidence
        }
