from nexus_reliability_v2 import NexusReliabilityV2

r=NexusReliabilityV2()
r.record_success("PROCESS")
r.record_success("PROCESS")
r.record_failure("PROCESS","test failure")
r.record_success("THREAD")

print("NEXUS RELIABILITY V2 TEST")
print("PROCESS:",r.get_history("PROCESS"))
print("PROCESS reliability:",r.reliability("PROCESS"))
print("THREAD:",r.get_history("THREAD"))
print("THREAD reliability:",r.reliability("THREAD"))
print("PASS:",r.reliability("PROCESS")==2/3 and r.reliability("THREAD")==1.0)
