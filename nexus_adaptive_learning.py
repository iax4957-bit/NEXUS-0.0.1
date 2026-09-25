class NexusAdaptiveLearning:
    def __init__(self, backends=None):
        if backends is None:
            backends = [
                "PROCESS",
                "THREAD",
                "SEQUENTIAL"
            ]

        self.backends = backends

    def choose_backend(self, history, task_type):
        known = set(history.keys())

        for backend in self.backends:
            if backend not in known:
                return backend

        if not history:
            if task_type == "CPU":
                return "PROCESS"

            if task_type == "IO":
                return "THREAD"

            return "SEQUENTIAL"

        return min(
            history,
            key=lambda backend:
                history[backend]["best_time"]
        )
