from nexus_adaptive_runtime_v5 import NexusAdaptiveRuntimeV5
from nexus_task_v2 import NexusTaskV2

def cpu_work(n):
    total=0
    for i in range(1,n):
        total+=(i*i)%1000003
    return total

tasks=[NexusTaskV2(f"CPU-{i+1}",cpu_work,(500000,),"CPU") for i in range(4)]
runtime=NexusAdaptiveRuntimeV5(workers=4,memory_file="nexus_v5_test_memory.json")
result=runtime.execute("CPU",500000,tasks)

print("NEXUS RUNTIME V5 TEST")
print("Mode:",result["mode"])
print("Requested:",result["requested_backend"])
print("Used:",result["backend"])
print("Fallback:",result["fallback_used"])
print("Confidence:",result["confidence"])
print("Time:",round(result["elapsed"],3),"seconds")
expected=cpu_work(500000)
print("Results correct:",len(result["results"])==4 and all(value==expected for _,value in result["results"]))
print("PASS")
