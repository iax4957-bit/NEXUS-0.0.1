from nexus_adaptive_learning_v4 import NexusAdaptiveLearningV4
import time
l=NexusAdaptiveLearningV4()
h={"PROCESS":{"average_time":0.30,"best_time":0.30,"runs":3,"last_run":time.time()},"THREAD":{"average_time":0.20,"best_time":0.20,"runs":3,"last_run":time.time()}}
print(l.decide(h,"CPU"))
