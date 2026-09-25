from nexus_adaptive_runtime_v4 import NexusAdaptiveRuntimeV4
from nexus_task_v2 import NexusTaskV2

FILE="test_nexus_runtime_v4.json"

def cpu_work(n):
    total=0
    for i in range(1,n):
        total += (i*i)%1000003
    return total

def make_tasks():
    return [NexusTaskV2("T"+str(i+1),cpu_work,args=(1000000,),task_type="CPU") for i in range(4)]

runtime=NexusAdaptiveRuntimeV4(workers=4,memory_file=FILE)

for run in range(1,4):
    result=runtime.execute("CPU",1000000,make_tasks())
    print("RUN",run,"=>",result["mode"],result["backend"],f"{result["elapsed"]:.3f}s")

print("PASS" if result["backend"]=="PROCESS" and len(result["results"])==4 else "FAIL")
