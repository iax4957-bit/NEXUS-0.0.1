from nexus_reliability import NexusReliability

r=NexusReliability()
r.record_error("PROCESS","test failure")
print("RELIABILITY TEST")
print("Has errors:",r.has_errors())
print("Errors:",r.get_errors())
print("PASS" if r.has_errors() else "FAIL")
