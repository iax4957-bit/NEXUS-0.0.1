class NexusReliabilityConfidenceV1:

    def __init__(self, min_samples=10):
        self.min_samples = min_samples

    def calculate(self, successes, failures):
        successes = max(0, int(successes))
        failures = max(0, int(failures))

        total = successes + failures

        if total == 0:
            return 0.0

        reliability = successes / total

        confidence = min(
            total / self.min_samples,
            1.0
        )

        return confidence

    def evaluate(self, successes, failures):
        successes = max(0, int(successes))
        failures = max(0, int(failures))

        total = successes + failures

        if total == 0:
            return {
                "reliability": None,
                "samples": 0,
                "confidence": 0.0
            }

        reliability = successes / total

        confidence = self.calculate(
            successes,
            failures
        )

        return {
            "reliability": reliability,
            "samples": total,
            "confidence": confidence
        }
