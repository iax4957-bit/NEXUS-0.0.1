import hashlib
import json

from nexus_adaptive_runtime_v11 import NexusAdaptiveRuntimeV11


class NexusAdaptiveRuntimeV12(NexusAdaptiveRuntimeV11):

    def __init__(
        self,
        workers=4,
        batch_size=10,
        memory_file="nexus_performance_v3.json",
        reliability_file="nexus_reliability_v3.json"
    ):
        super().__init__(
            workers=workers,
            batch_size=batch_size,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

        self.cache = {}

    def _cache_key(self, task_type, workload_size, tasks):
        values = []

        for task in tasks:
            values.append({
                "task_id": getattr(task, "task_id", None),
                "value": getattr(task, "value", None)
            })

        payload = {
            "task_type": task_type,
            "workload_size": workload_size,
            "tasks": values
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
            default=str
        ).encode()

        return hashlib.sha256(encoded).hexdigest()

    def cache_get(self, key):
        return self.cache.get(key)

    def cache_set(self, key, value):
        self.cache[key] = value

    def cache_clear(self):
        self.cache.clear()

    def execute_batched_cached(
        self,
        task_type,
        workload_size,
        tasks
    ):
        tasks = list(tasks)

        key = self._cache_key(
            task_type,
            workload_size,
            tasks
        )

        cached = self.cache_get(key)

        if cached is not None:
            return {
                **cached,
                "cache_hit": True
            }

        result = self.execute_batched(
            task_type,
            workload_size,
            tasks
        )

        cached_result = dict(result)
        cached_result["cache_hit"] = False

        self.cache_set(key, cached_result)

        return cached_result

    def execute_auto_batched_cached(
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

        result = self.execute_batched_cached(
            learning_task_type,
            workload_size,
            tasks
        )

        result["classification"] = classification
        result["classified_task_type"] = task_type
        result["learning_task_type"] = learning_task_type

        return result
