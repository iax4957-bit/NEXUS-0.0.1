import json
import os


class NexusReliabilityV3:

    def __init__(self, filename="nexus_reliability_v3.json"):
        self.filename = filename
        self.history = {}
        self.load()

    def load(self):
        if not os.path.exists(self.filename):
            self.history = {}
            return

        try:
            with open(self.filename, "r") as file:
                data = json.load(file)

            if isinstance(data, dict):
                self.history = data
            else:
                self.history = {}

        except (json.JSONDecodeError, OSError):
            self.history = {}

    def save(self):
        with open(self.filename, "w") as file:
            json.dump(
                self.history,
                file,
                indent=4
            )

    def _get_backend(self, backend):
        return self.history.setdefault(
            str(backend),
            {
                "successes": 0,
                "failures": 0
            }
        )

    def record_success(self, backend):
        data = self._get_backend(backend)
        data["successes"] += 1
        self.save()

    def record_failure(self, backend, error=None):
        data = self._get_backend(backend)
        data["failures"] += 1
        self.save()

    def reliability(self, backend):
        data = self.history.get(
            str(backend)
        )

        if not data:
            return None

        successes = data.get("successes", 0)
        failures = data.get("failures", 0)

        total = successes + failures

        if total == 0:
            return None

        return successes / total

    def get_history(self, backend):
        return self.history.get(
            str(backend),
            {
                "successes": 0,
                "failures": 0
            }
        )

    def get_all_history(self):
        return self.history
