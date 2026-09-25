from nexus_reliability import NexusReliability

class NexusFallback:
    def __init__(self,backends):
        self.backends=backends
        self.reliability=NexusReliability()

    def execute(self,task):
        for backend,executor in self.backends:
            try:
                return backend,executor(task)
            except Exception as error:
                self.reliability.record_error(backend,error)
        raise RuntimeError("All backends failed")
