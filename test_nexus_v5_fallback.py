from nexus_adaptive_runtime_v5 import NexusAdaptiveRuntimeV5
from nexus_task_v2 import NexusTaskV2

def simple_work(x):
    return x*x

runtime=NexusAdaptiveRuntimeV5(workers=4,memory_file="nexus_v5_fallback_test.json")
original=runtime._execute_backend
def failing_process(backend,tasks):
    if backend=="PROCESS":
        raise RuntimeError("Simulated PROCESS failure")
    return original(backend,tasks)
runtime._execute_backend=failing_process
tasks=[NexusTaskV2(f"T{i+1}",simple_work,(i+1,),"CPU") for i in range(4)]

result=runtime.execute("CPU",4,tasks)
print("NEXUS V5 FALLBACK TEST")
print("Requested:",result["requested_backend"])
print("Used:",result["backend"])
print("Fallback:",result["fallback_used"])
print("Errors:",result["errors"])
print("Results:",result["results"])
print("PASS:",result["fallback_used"] and result["backend"]!="PROCESS" and len(result["errors"])>0)
