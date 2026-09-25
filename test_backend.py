from nexus_backend import NexusThreadBackend


class TestTask:
    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 2


tasks = [
    TestTask("T1", 10),
    TestTask("T2", 20),
    TestTask("T3", 30),
    TestTask("T4", 40),
]

backend = NexusThreadBackend(workers=4)

results = backend.execute(tasks)

print("NEXUS BACKEND TEST")

for task_id, result in results:
    print(task_id, "=>", result)
