class NexusReliabilityV2:
    def __init__(self):
        self.history={}

    def record_success(self,backend):
        data=self.history.setdefault(backend,{"successes":0,"failures":0})
        data["successes"]+=1

    def record_failure(self,backend,error):
        data=self.history.setdefault(backend,{"successes":0,"failures":0})
        data["failures"]+=1

    def reliability(self,backend):
        data=self.history.get(backend)
        if not data:
            return 1.0
        total=data["successes"]+data["failures"]
        if total==0:
            return 1.0
        return data["successes"]/total

    def get_history(self,backend):
        return self.history.get(backend,{"successes":0,"failures":0})
