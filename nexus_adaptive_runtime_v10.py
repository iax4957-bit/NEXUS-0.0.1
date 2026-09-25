import time

from nexus_adaptive_runtime_v9 import NexusAdaptiveRuntimeV9
from nexus_task_classifier_v1 import NexusTaskClassifierV1


class NexusAdaptiveRuntimeV10(NexusAdaptiveRuntimeV9):

    def __init__(
        self,
        workers=4,
        memory_file="nexus_performance_v3.json",
        reliability_file="nexus_reliability_v3.json"
    ):
        super().__init__(
            workers=workers,
            memory_file=memory_file,
            reliability_file=reliability_file
        )
        self.classifier = NexusTaskClassifierV1()

    def classify_task(
        self,
        workload_size,
        cpu_ratio=0.0,
        io_ratio=0.0
    ):
        return self.classifier.classify(
            workload_size=workload_size,
            cpu_ratio=cpu_ratio,
            io_ratio=io_ratio
        )

    def execute_auto(
        self,
        workload_size,
        tasks,
        cpu_ratio=0.0,
        io_ratio=0.0
    ):
        classification = self.classify_task(
            workload_size,
            cpu_ratio,
            io_ratio
        )

        task_type = classification["task_type"]

        learning_task_type = (
            "CPU" if task_type == "SMALL"
            else task_type
        )

        result = self.execute(
            learning_task_type,
            workload_size,
            tasks
        )

        result["classification"] = classification
        result["classified_task_type"] = task_type
        result["learning_task_type"] = learning_task_type

        return result
