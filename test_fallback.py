from nexus_fallback import NexusFallback

def failed(task):
    raise RuntimeError("PROCESS unavailable")

def backup(task):
    return task*2

fallback=NexusFallback([("PROCESS",failed),("THREAD",backup)])
backend,result=fallback.execute(21)
print("FALLBACK TEST")
print("Selected backend:",backend)
print("Result:",result)
print("Errors:",fallback.reliability.get_errors())
print("PASS" if backend=="THREAD" and result==42 else "FAIL")
