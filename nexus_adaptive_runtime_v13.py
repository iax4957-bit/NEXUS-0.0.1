import random

from nexus_adaptive_runtime_v12 import NexusAdaptiveRuntimeV12


class NexusAdaptiveRuntimeV13(NexusAdaptiveRuntimeV12):

    def __init__(
        self,
        workers=4,
        batch_size=10,
        exploration_rate=0.2,
        memory_file="nexus_performance_v3.json",
        reliability_file="nexus_reliability_v3.json"
    ):
        super().__init__(
            workers=workers,
            batch_size=batch_size,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

        self.exploration_rate = max(
            0.0,
            min(float(exploration_rate), 1.0)
        )

    def _exploration_backend(self, preferred):
        backends = [
            "PROCESS",
            "THREAD",
            "SEQUENTIAL"
        ]

        alternatives = [
            backend
            for backend in backends
            if backend != preferred
        ]

        if not alternatives:
            return preferred

        return random.choice(alternatives)

    def choose_with_exploration(
        self,
        history,
        task_type,
        force_exploration=False
    ):
        selected, learning_decision = self._choose_backend(
            history,
            task_type
        )

        preferred = selected["backend"]

        should_explore = (
            force_exploration
            or random.random() < self.exploration_rate
        )

        if should_explore:
            backend = self._exploration_backend(preferred)
            mode = "EXPLORE"
        else:
            backend = preferred
            mode = "EXPLOIT"

        return {
            "backend": backend,
            "preferred_backend": preferred,
            "mode": mode,
            "exploration": should_explore,
            "learning_decision": learning_decision
        }
