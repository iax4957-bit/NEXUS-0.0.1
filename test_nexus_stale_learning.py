import time
from nexus_adaptive_learning_v4 import NexusAdaptiveLearningV4

now=time.time()
history={"PROCESS":{"average_time":0.3,"runs":5,"last_run":now-1000},"THREAD":{"average_time":2.4,"runs":5,"last_run":now-1000},"SEQUENTIAL":{"average_time":1.1,"runs":5,"last_run":now-1000}}
learning=NexusAdaptiveLearningV4(max_age=300,min_runs=3)
decision=learning.decide(history,"CPU")
print("STALE DATA TEST")
print("Decision:",decision)
