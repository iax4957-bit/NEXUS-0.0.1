class NexusReliability:
    def __init__(self):
        self.errors=[]

    def record_error(self,backend,error):
        self.errors.append({"backend":backend,"error":str(error)})

    def has_errors(self):
        return len(self.errors)>0

    def get_errors(self):
        return self.errors
