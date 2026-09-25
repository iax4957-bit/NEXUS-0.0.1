import time
from nexus_performance_memory_v3 import NexusPerformanceMemoryV3
from nexus_process_backend import NexusProcessBackend
from nexus_backend import NexusThreadBackend
from nexus_task_v2 import NexusTaskV2
FILE="test_nexus_repeated_learning.json"

def cpu_work(n):
    total=0
    for i in range(1,n):
        total+=(i*i)%1000003
    return total

def make_tasks():
    return [NexusTaskV2("R1",cpu_work,args=(1000000,),task_type="CPU"),NexusTaskV2("R2",cpu_work,args=(1000000,),task_type="CPU"),NexusTaskV2("R3",cpu_work,args=(1000000,),task_type="CPU"),NexusTaskV2("R4",cpu_work,args=(1000000,),task_type="CPU")]

memory=NexusPerformanceMemoryV3(FILE)

for backend in ["PROCESS","THREAD"]:
    print("TESTING",backend)
    for run in range(1,4):
        tasks=make_tasks()
        start=time.perf_counter()
        if backend=="PROCESS":
            NexusProcessBackend(4).execute(tasks)
        else:
            NexusThreadBackend(4).execute(tasks)
        elapsed=time.perf_counter()-start
        memory.record("CPU",1000000,4,backend,elapsed)
        print(f"Run {run}: {elapsed:.3f}s")

history=memory.get_history("CPU",1000000,4)
print("FINAL HISTORY:",history)
print("BEST BACKEND:",memory.best_backend("CPU",1000000,4))
