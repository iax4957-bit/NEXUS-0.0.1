class NexusReliabilitySelector:
    def __init__(self,min_reliability=0.5):
        self.min_reliability=min_reliability

    def choose(self,backends,reliability):
        valid=[b for b in backends if reliability.get(b,1.0)>=self.min_reliability]
        if not valid:
            return None
        return max(valid,key=lambda b:reliability.get(b,1.0))
