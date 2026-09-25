import time
from nexus_performance_memory_v3 import NexusPerformanceMemoryV3
from nexus_process_backend import NexusProcessBackend
from nexus_backend import NexusThreadBackend
from nexus_task_v2 import NexusTaskV2
FILE="test_nexus_real_learning.json"

def cpu_work(n):
    total=0
    for i in range(1,n):
        total+=(i*i)%1000003
    return total

def make_tasks():
    return [NexusTaskV2("REAL-1",cpu_work,args=(1000000,),task_type="CPU"),NexusTaskV2("REAL-2",cpu_work,args=(1000000,),task_type="CPU"),NexusTaskV2("REAL-3",cpu_work,args=(1000000,),task_type="CPU"),NexusTaskV2("REAL-4",cpu_work,args=(1000000,),task_type="CPU")]

memory=NexusPerformanceMemoryV3(FILE)

for backend in ["PROCESS","THREAD"]:
    tasks=make_tasks()
    start=time.perf_counter()
    if backend=="PROCESS":
        NexusProcessBackend(4).execute(tasks)
    else:
        NexusThreadBackend(4).execute(tasks)
    elapsed=time.perf_counter()-start
    memory.record("CPU",1000000,4,backend,elapsed)
    print(f"{backend}: {elapsed:.3f}s")

history=memory.get_history("CPU",1000000,4)
print("REAL HISTORY:",history)
best=memory.best_backend("CPU",1000000,4)
print("BEST BACKEND:",best)
