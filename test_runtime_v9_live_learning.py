import os
import tempfile

from nexus_adaptive_runtime_v9 import NexusAdaptiveRuntimeV9


class FakeBackendRuntime(NexusAdaptiveRuntimeV9):

    def __init__(self, memory_file, reliability_file):
        super().__init__(
            workers=2,
            memory_file=memory_file,
            reliability_file=reliability_file
        )

        self.execution_count = {
            "PROCESS": 0,
            "THREAD": 0,
            "SEQUENTIAL": 0
        }

    def _execute_backend(self, backend, tasks):

        self.execution_count[backend] += 1

        # محاكاة نتائج تنفيذ صحيحة
        return [
            (task.task_id, task.run())
            for task in tasks
        ]


class Task:

    def __init__(self, task_id, value):
        self.task_id = task_id
        self.value = value

    def run(self):
        return self.value * 10


# ==========================================
# ملفات مؤقتة للاختبار
# ==========================================

memory_file = tempfile.mktemp(
    prefix="nexus_v9_memory_",
    suffix=".json"
)

reliability_file = tempfile.mktemp(
    prefix="nexus_v9_reliability_",
    suffix=".json"
)


runtime = FakeBackendRuntime(
    memory_file,
    reliability_file
)


tasks = [
    Task(1, 3),
    Task(2, 6),
    Task(3, 9)
]


print("=== LIVE LEARNING TEST ===")
print()


# ==========================================
# المرحلة الأولى
# لا توجد معرفة سابقة
# ==========================================

print("RUN 1")

result_1 = runtime.execute(
    "CPU",
    3,
    tasks
)

print("BACKEND:", result_1["backend"])
print("FALLBACK:", result_1["fallback_used"])
print("RESULTS:", result_1["results"])

print()


# ==========================================
# المرحلة الثانية
# تنفيذ حقيقي مرة أخرى
# ==========================================

print("RUN 2")

result_2 = runtime.execute(
    "CPU",
    3,
    tasks
)

print("BACKEND:", result_2["backend"])
print("FALLBACK:", result_2["fallback_used"])
print("RESULTS:", result_2["results"])

print()


# ==========================================
# المرحلة الثالثة
# ==========================================

print("RUN 3")

result_3 = runtime.execute(
    "CPU",
    3,
    tasks
)

print("BACKEND:", result_3["backend"])
print("FALLBACK:", result_3["fallback_used"])
print("RESULTS:", result_3["results"])

print()


# ==========================================
# التحقق من التعلم
# ==========================================

history = runtime.memory.get_history(
    "CPU",
    3,
    2
)

print("=== PERFORMANCE MEMORY ===")
print(history)

print()


# ==========================================
# التحقق من Reliability
# ==========================================

print("=== RELIABILITY ===")

for backend in [
    "PROCESS",
    "THREAD",
    "SEQUENTIAL"
]:

    print(
        backend,
        runtime.reliability.get_history(
            backend
        )
    )

print()


# ==========================================
# التحقق من صحة النتائج
# ==========================================

expected = [
    (1, 30),
    (2, 60),
    (3, 90)
]

correct = (
    result_1["results"] == expected
    and
    result_2["results"] == expected
    and
    result_3["results"] == expected
)

memory_created = os.path.exists(
    memory_file
)

reliability_created = os.path.exists(
    reliability_file
)

print("RESULTS CORRECT:", correct)
print("MEMORY PERSISTED:", memory_created)
print(
    "RELIABILITY PERSISTED:",
    reliability_created
)

print()
print(
    "PASS:",
    correct
    and memory_created
    and reliability_created
)
