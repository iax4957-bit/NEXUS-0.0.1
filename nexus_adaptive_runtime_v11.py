from nexus_adaptive_runtime_v10 import NexusAdaptiveRuntimeV10


class NexusAdaptiveRuntimeV11(NexusAdaptiveRuntimeV10):

    def __init__(
        self,
        workers=4,
        batch_size=10,
        memory_file="nexus_performance_v3.json",
        reliability_file="nexus_reliability_v3.json"
    ):
        super().__init__(
            workers=workers,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

        self.batch_size = max(1, int(batch_size))

    def create_batches(self, tasks):
        tasks = list(tasks)

        return [
            tasks[i:i + self.batch_size]
            for i in range(0, len(tasks), self.batch_size)
        ]

    def execute_batched(
        self,
        task_type,
        workload_size,
        tasks
    ):
        batches = self.create_batches(tasks)

        all_results = []

        for batch in batches:
            result = self.execute(
                task_type,
                len(batch),
                batch
            )

            all_results.extend(result["results"])

        return {
            "task_type": task_type,
            "batch_size": self.batch_size,
            "batch_count": len(batches),
            "task_count": len(tasks),
            "results": all_results
        }

    def execute_auto_batched(
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

        result = self.execute_batched(
            learning_task_type,
            workload_size,
            tasks
        )

        result["classification"] = classification
        result["classified_task_type"] = task_type
        result["learning_task_type"] = learning_task_type

        return result
