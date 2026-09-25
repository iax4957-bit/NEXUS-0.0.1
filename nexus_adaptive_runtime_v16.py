import os
import json
import time
import statistics

from nexus_adaptive_runtime_v13 import NexusAdaptiveRuntimeV13


class NexusAdaptiveRuntimeV16(NexusAdaptiveRuntimeV13):

    DEFAULT_WORKERS = [1, 2, 3, 4]

    def __init__(
        self,
        workers=4,
        batch_size=1000000,
        exploration_rate=0.0,
        memory_file="nexus_performance_v3.json",
        reliability_file="nexus_reliability_v3.json",
        worker_memory_file="nexus_worker_learning_v16.json"
    ):
        super().__init__(
            workers=workers,
            batch_size=batch_size,
            exploration_rate=exploration_rate,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

        self.worker_memory_file = worker_memory_file
        self.worker_memory = {}
        self.load_worker_memory()

    # --------------------------------------------------
    # Worker learning memory
    # --------------------------------------------------

    def load_worker_memory(self):
        if not os.path.exists(self.worker_memory_file):
            self.worker_memory = {}
            return

        try:
            with open(self.worker_memory_file, "r") as file:
                self.worker_memory = json.load(file)
        except Exception:
            self.worker_memory = {}

    def save_worker_memory(self):
        with open(self.worker_memory_file, "w") as file:
            json.dump(self.worker_memory, file, indent=4)

    def _key(self, task_type, workload_size):
        return f"{task_type}:{int(workload_size)}"

    def _get_record(self, task_type, workload_size, workers):
        key = self._key(task_type, workload_size)

        data = self.worker_memory.setdefault(key, {})

        return data.setdefault(
            str(workers),
            {
                "runs": 0,
                "times": [],
                "average_time": None,
                "correct": True
            }
        )

    # --------------------------------------------------
    # Measure one worker configuration
    # --------------------------------------------------

    def _measure_worker(self, task_type, workload_size, tasks, workers):

        start = time.perf_counter()

        runtime = NexusAdaptiveRuntimeV16(
            workers=workers,
            batch_size=self.batch_size,
            exploration_rate=0.0,
            memory_file=self.memory.filename,
            reliability_file=self.reliability.filename,
            worker_memory_file=self.worker_memory_file
        )

        result = runtime.execute(
            task_type=task_type,
            workload_size=workload_size,
            tasks=tasks
        )

        elapsed = time.perf_counter() - start

        return elapsed, result["results"]

    # --------------------------------------------------
    # Learn workers
    # --------------------------------------------------

    def learn_workers(
        self,
        task_type,
        workload_size,
        tasks,
        worker_counts=None
    ):

        worker_counts = worker_counts or self.DEFAULT_WORKERS

        measurements = []

        reference_results = None

        for workers in worker_counts:

            elapsed, results = self._measure_worker(
                task_type,
                workload_size,
                tasks,
                workers
            )

            # First result becomes correctness reference
            if reference_results is None:
                reference_results = results

            correct = results == reference_results

            record = self._get_record(
                task_type,
                workload_size,
                workers
            )

            record["runs"] += 1
            record["times"].append(elapsed)

            # Keep memory bounded
            record["times"] = record["times"][-20:]

            record["average_time"] = statistics.mean(
                record["times"]
            )

            record["correct"] = bool(
                record.get("correct", True) and correct
            )

            self.save_worker_memory()

            measurements.append({
                "workers": workers,
                "elapsed": elapsed,
                "correct": correct
            })

        valid = [
            item
            for item in measurements
            if item["correct"]
        ]

        if not valid:
            raise RuntimeError(
                "NEXUS V16: no worker configuration "
                "passed correctness validation"
            )

        best = min(
            valid,
            key=lambda item: item["elapsed"]
        )

        return {
            "selected_workers": best["workers"],
            "measurements": measurements,
            "correct": all(
                item["correct"]
                for item in measurements
            )
        }

    # --------------------------------------------------
    # Choose learned worker count
    # --------------------------------------------------

    def choose_workers(
        self,
        task_type,
        workload_size,
        available_workers=None
    ):

        available_workers = (
            available_workers or self.DEFAULT_WORKERS
        )

        key = self._key(
            task_type,
            workload_size
        )

        data = self.worker_memory.get(key, {})

        valid = []

        for workers in available_workers:

            record = data.get(str(workers))

            if not record:
                continue

            if not record.get("correct", False):
                continue

            average = record.get("average_time")

            if average is None:
                continue

            valid.append(
                (workers, average)
            )

        if not valid:
            return {
                "workers": None,
                "mode": "EXPLORE",
                "reason": "no_worker_history"
            }

        workers, average = min(
            valid,
            key=lambda item: item[1]
        )

        return {
            "workers": workers,
            "average_time": average,
            "mode": "EXPLOIT",
            "reason": "best_correct_worker"
        }

    # --------------------------------------------------
    # Adaptive execution
    # --------------------------------------------------

    def execute_adaptive(
        self,
        task_type,
        workload_size,
        tasks,
        worker_counts=None,
        learn_if_missing=True
    ):

        decision = self.choose_workers(
            task_type,
            workload_size,
            worker_counts
        )

        if (
            decision["workers"] is None
            and learn_if_missing
        ):

            learning = self.learn_workers(
                task_type,
                workload_size,
                tasks,
                worker_counts
            )

            selected_workers = learning[
                "selected_workers"
            ]

            mode = "EXPLORE"

        else:

            selected_workers = decision["workers"]
            learning = None
            mode = "EXPLOIT"

        # Final execution using learned configuration
        runtime = NexusAdaptiveRuntimeV16(
            workers=selected_workers,
            batch_size=self.batch_size,
            exploration_rate=0.0,
            memory_file=self.memory.filename,
            reliability_file=self.reliability.filename,
            worker_memory_file=self.worker_memory_file
        )

        start = time.perf_counter()

        result = runtime.execute(
            task_type=task_type,
            workload_size=workload_size,
            tasks=tasks
        )

        elapsed = time.perf_counter() - start

        return {
            "mode": mode,
            "workers": selected_workers,
            "elapsed": elapsed,
            "results": result["results"],
            "correctness_checked": True,
            "learning": learning
        }
