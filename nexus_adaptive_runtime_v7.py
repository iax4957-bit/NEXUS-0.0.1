import time

from nexus_adaptive_learning_v4 import NexusAdaptiveLearningV4
from nexus_performance_memory_v3 import NexusPerformanceMemoryV3
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend
from nexus_reliability_v3 import NexusReliabilityV3


class NexusAdaptiveRuntimeV7:

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

        # Reliability أصبحت دائمة
        self.reliability = NexusReliabilityV3(
            reliability_file
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

    def _choose_backend(
        self,
        history,
        task_type
    ):

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

            if not measurement:
                performance = None
            else:
                performance = measurement.get(
                    "average_time"
                )

            reliability = self._reliability_score(
                backend
            )

            scored.append({
                "backend": backend,
                "performance": performance,
                "reliability": reliability
            })

        # نستبعد Backend المعروف بأنه
        # غير موثوق بدرجة أقل من 50%
        reliable = [
            item
            for item in scored
            if (
                item["reliability"] is None
                or item["reliability"] >= 0.5
            )
        ]

        if not reliable:
            reliable = scored

        # إذا توفرت بيانات Performance
        # نستخدمها كأساس للقرار
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
                    )
                )
            )

            return best, learning_decision

        # لا توجد بيانات أداء
        # نعود إلى قرار Learning
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

                # تسجيل النجاح بشكل دائم
                self.reliability.record_success(
                    backend
                )

                # تسجيل الأداء
                self.memory.record(
                    task_type,
                    workload_size,
                    self.workers,
                    backend,
                    elapsed
                )

                return {
                    "mode":
                        learning_decision["mode"],

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
                        self.reliability.reliability(
                            backend
                        ),

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

                # تسجيل الفشل بشكل دائم
                self.reliability.record_failure(
                    backend,
                    error
                )

                last_error = error

        raise RuntimeError(
            "All NEXUS V7 backends failed"
        ) from last_error
