class NexusBackendSelector:
    def select(self, task_type):
        if task_type == "CPU":
            return "PROCESS"

        if task_type == "IO":
            return "THREAD"

        return "SEQUENTIAL"
