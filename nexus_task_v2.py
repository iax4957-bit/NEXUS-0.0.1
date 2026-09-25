class NexusTaskV2:
    def __init__(self, task_id, operation, args=(), task_type="SIMPLE"):
        self.task_id = task_id
        self.operation = operation
        self.args = args
        self.task_type = task_type
        self.result = None

    def run(self):
        self.result = self.operation(*self.args)
        return self.result
