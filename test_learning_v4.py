from nexus_adaptive_learning_v4 import NexusAdaptiveLearningV4
import time

l=NexusAdaptiveLearningV4()
h={}
print("EMPTY:",l.decide(h,"CPU"))
h["PROCESS"]={"average_time":0.30,"best_time":0.30,"runs":1,"last_run":time.time()}
print("1 RUN:",l.decide(h,"CPU"))
h["PROCESS"]["runs"]=3
print("3 RUNS:",l.decide(h,"CPU"))
