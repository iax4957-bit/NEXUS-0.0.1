import time
from nexus_adaptive_learning_v4 import NexusAdaptiveLearningV4
from nexus_performance_memory_v3 import NexusPerformanceMemoryV3
from nexus_backend import NexusThreadBackend
from nexus_process_backend import NexusProcessBackend
from nexus_reliability import NexusReliability

class NexusAdaptiveRuntimeV5:
    def __init__(self,workers=4,memory_file="nexus_performance_v3.json"):
        self.workers=workers
        self.memory=NexusPerformanceMemoryV3(memory_file)
        self.learning=NexusAdaptiveLearningV4()
        self.reliability=NexusReliability()

    def _execute_backend(self,backend,tasks):
        if backend=="PROCESS":
            return NexusProcessBackend(self.workers).execute(tasks)
        if backend=="THREAD":
            return NexusThreadBackend(self.workers).execute(tasks)
        if backend=="SEQUENTIAL":
            return [(task.task_id,task.run()) for task in tasks]
        raise ValueError(f"Unknown backend: {backend}")

    def execute(self,task_type,workload_size,tasks):
        history=self.memory.get_history(task_type,workload_size,self.workers)
        decision=self.learning.decide(history,task_type)
        preferred=decision["backend"]
        candidates=[preferred]+[b for b in ["PROCESS","THREAD","SEQUENTIAL"] if b!=preferred]
        last_error=None
        for backend in candidates:
            try:
                start=time.perf_counter()
                results=self._execute_backend(backend,tasks)
                elapsed=time.perf_counter()-start
                self.memory.record(task_type,workload_size,self.workers,backend,elapsed)
                return {"mode":decision["mode"],"requested_backend":preferred,"backend":backend,"fallback_used":backend!=preferred,"confidence":decision["confidence"],"elapsed":elapsed,"results":results,"errors":self.reliability.get_errors()}
            except Exception as error:
                self.reliability.record_error(backend,error)
                last_error=error
        raise RuntimeError("All NEXUS backends failed") from last_error
