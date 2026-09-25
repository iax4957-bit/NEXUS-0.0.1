from nexus_reliability_selector import NexusReliabilitySelector
s=NexusReliabilitySelector(0.5)
r={"PROCESS":0.4,"THREAD":1.0,"SEQUENTIAL":0.8}
print(s.choose(["PROCESS","THREAD","SEQUENTIAL"],r))
