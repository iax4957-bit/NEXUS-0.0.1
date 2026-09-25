import time
from nexus_adaptive_runtime_v4 import NexusAdaptiveRuntimeV4
from nexus_performance_memory_v3 import NexusPerformanceMemoryV3
from nexus_task_v2 import NexusTaskV2

FILE="test_nexus_adaptation.json"
m=NexusPerformanceMemoryV3(FILE)
m.record("CPU",1000000,4,"PROCESS",0.30)
m.record("CPU",1000000,4,"PROCESS",0.30)
m.record("CPU",1000000,4,"PROCESS",0.30)
m.record("CPU",1000000,4,"THREAD",0.20)
m.record("CPU",1000000,4,"THREAD",0.20)
m.record("CPU",1000000,4,"THREAD",0.20)

def cpu_work(n):
    total=0
    for i in range(1,n):
        total+=(i*i)%1000003
    return total

tasks=[NexusTaskV2("ADAPT-1",cpu_work,args=(1000000,),task_type="CPU")]
runtime=NexusAdaptiveRuntimeV4(workers=4,memory_file=FILE)
result=runtime.execute("CPU",1000000,tasks)

print("NEXUS ADAPTATION TEST")
print("Mode:",result["mode"])
print("Selected backend:",result["backend"])
print("Confidence:",result["confidence"])
print(f"Actual execution: {result["elapsed"]:.3f}s")
print("PASS" if result["backend"]=="THREAD" and result["mode"]=="EXPLOIT" else "FAIL")
