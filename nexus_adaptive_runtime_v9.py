import time

from nexus_adaptive_learning_v4 import NexusAdaptiveLearningV4
from nexus_performance_memory_v3 import NexusPerformanceMemoryV3
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend
from nexus_reliability_v3 import NexusReliabilityV3
from nexus_reliability_confidence_v1 import NexusReliabilityConfidenceV1


class NexusAdaptiveRuntimeV9:

    RELIABILITY_THRESHOLD = 0.5
    CONFIDENCE_THRESHOLD = 0.5

    def __init__(
        self,
        workers=4,
        memory_file="nexus_performance_v3.json",
        reliability_file="nexus_reliability_v3.json"
    ):
        self.workers = workers

        self.memory = NexusPerformanceMemoryV3(
            memory_file
        )

        self.learning = NexusAdaptiveLearningV4()

        self.reliability = NexusReliabilityV3(
            reliability_file
        )

        self.confidence = NexusReliabilityConfidenceV1(
            min_samples=10
        )

    def _execute_backend(self, backend, tasks):

        if backend == "PROCESS":
            return NexusProcessBackend(
                self.workers
            ).execute(tasks)

        if backend == "THREAD":
            return NexusThreadBackend(
                self.workers
            ).execute(tasks)

        if backend == "SEQUENTIAL":
            return [
                (task.task_id, task.run())
                for task in tasks
            ]

        raise ValueError(
            f"Unknown backend: {backend}"
        )

    def _reliability_score(self, backend):
        return self.reliability.reliability(
            backend
        )

    def _confidence_score(self, backend):

        history = self.reliability.get_history(
            backend
        )

        return self.confidence.evaluate(
            history.get("successes", 0),
            history.get("failures", 0)
        )

    def _choose_backend(self, history, task_type):

        learning_decision = self.learning.decide(
            history,
            task_type
        )

        preferred = learning_decision["backend"]

        candidates = [
            preferred,
            *[
                backend
                for backend in [
                    "PROCESS",
                    "THREAD",
                    "SEQUENTIAL"
                ]
                if backend != preferred
            ]
        ]

        scored = []

        for backend in candidates:

            measurement = history.get(
                backend
            )

            performance = (
                measurement.get("average_time")
                if measurement
                else None
            )

            reliability = self._reliability_score(
                backend
            )

            confidence_data = (
                self._confidence_score(backend)
            )

            confidence = confidence_data[
                "confidence"
            ]

            scored.append({
                "backend": backend,
                "performance": performance,
                "reliability": reliability,
                "confidence": confidence,
                "samples": confidence_data[
                    "samples"
                ]
            })

        reliable = [
            item
            for item in scored
            if (
                item["reliability"] is None
                or (
                    item["reliability"]
                    > self.RELIABILITY_THRESHOLD
                    and
                    item["confidence"]
                    >= self.CONFIDENCE_THRESHOLD
                )
            )
        ]

        if not reliable:
            reliable = scored

        with_performance = [
            item
            for item in reliable
            if item["performance"] is not None
        ]

        if with_performance:

            best = min(
                with_performance,
                key=lambda item: (
                    item["performance"],
                    -(
                        item["reliability"]
                        if item["reliability"]
                        is not None
                        else 0.0
                    ),
                    -item["confidence"]
                )
            )

            return best, learning_decision

        for item in reliable:

            if item["backend"] == preferred:
                return item, learning_decision

        return reliable[0], learning_decision

    def execute(
        self,
        task_type,
        workload_size,
        tasks
    ):

        history = self.memory.get_history(
            task_type,
            workload_size,
            self.workers
        )

        selected, learning_decision = (
            self._choose_backend(
                history,
                task_type
            )
        )

        preferred = selected["backend"]

        candidates = [
            preferred,
            *[
                backend
                for backend in [
                    "PROCESS",
                    "THREAD",
                    "SEQUENTIAL"
                ]
                if backend != preferred
            ]
        ]

        last_error = None

        for backend in candidates:

            try:

                start = time.perf_counter()

                results = self._execute_backend(
                    backend,
                    tasks
                )

                elapsed = (
                    time.perf_counter()
                    - start
                )

                self.reliability.record_success(
                    backend
                )

                self.memory.record(
                    task_type,
                    workload_size,
                    self.workers,
                    backend,
                    elapsed
                )

                reliability = (
                    self.reliability.reliability(
                        backend
                    )
                )

                confidence_data = (
                    self._confidence_score(
                        backend
                    )
                )

                return {
                    "mode":
                        learning_decision[
                            "mode"
                        ],

                    "requested_backend":
                        preferred,

                    "backend":
                        backend,

                    "fallback_used":
                        backend != preferred,

                    "confidence":
                        learning_decision[
                            "confidence"
                        ],

                    "reliability":
                        reliability,

                    "reliability_confidence":
                        confidence_data[
                            "confidence"
                        ],

                    "reliability_samples":
                        confidence_data[
                            "samples"
                        ],

                    "elapsed":
                        elapsed,

                    "results":
                        results,

                    "errors":
                        self.reliability.get_history(
                            backend
                        )
                }

            except Exception as error:

                self.reliability.record_failure(
                    backend,
                    error
                )

                last_error = error

        raise RuntimeError(
            "All NEXUS V9 backends failed"
        ) from last_error
