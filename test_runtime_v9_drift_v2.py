from nexus_adaptive_runtime_v9 import NexusAdaptiveRuntimeV9


class FakeLearning:

    def decide(self, history, task_type):
        best = min(
            history,
            key=lambda backend: history[backend]["average_time"]
        )

        return {
            "mode": "EXPLOIT",
            "backend": best,
            "reason": "test",
            "confidence": 1.0
        }


class FakeRuntime(NexusAdaptiveRuntimeV9):

    def __init__(self):
        self.learning = FakeLearning()

    def _reliability_score(self, backend):
        return 1.0

    def _confidence_score(self, backend):
        return {
            "reliability": 1.0,
            "samples": 10,
            "confidence": 1.0
        }


runtime = FakeRuntime()


# ==========================================
# PHASE 1
# PROCESS هو الأسرع
# ==========================================

history_phase_1 = {
    "PROCESS": {
        "average_time": 0.01,
        "runs": 20,
        "last_run": 9999999999
    },
    "THREAD": {
        "average_time": 0.10,
        "runs": 20,
        "last_run": 9999999999
    },
    "SEQUENTIAL": {
        "average_time": 0.20,
        "runs": 20,
        "last_run": 9999999999
    }
}

selected_1, learning_1 = runtime._choose_backend(
    history_phase_1,
    "CPU"
)

print("PHASE 1")
print("LEARNING:", learning_1["backend"])
print("SELECTED:", selected_1["backend"])


# ==========================================
# PHASE 2
# PROCESS أصبح أبطأ
# THREAD أصبح الأسرع
# ==========================================

history_phase_2 = {
    "PROCESS": {
        "average_time": 0.50,
        "runs": 20,
        "last_run": 9999999999
    },
    "THREAD": {
        "average_time": 0.05,
        "runs": 20,
        "last_run": 9999999999
    },
    "SEQUENTIAL": {
        "average_time": 0.20,
        "runs": 20,
        "last_run": 9999999999
    }
}

selected_2, learning_2 = runtime._choose_backend(
    history_phase_2,
    "CPU"
)

print()
print("PHASE 2")
print("LEARNING:", learning_2["backend"])
print("SELECTED:", selected_2["backend"])


# ==========================================
# RESULT
# ==========================================

changed = (
    selected_1["backend"] != selected_2["backend"]
)

print()
print("PERFORMANCE DRIFT DETECTED:", changed)
print("PHASE 1 BACKEND:", selected_1["backend"])
print("PHASE 2 BACKEND:", selected_2["backend"])
print()
print("PASS:", changed)
