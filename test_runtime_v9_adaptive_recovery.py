from nexus_adaptive_runtime_v9 import NexusAdaptiveRuntimeV9


class FakeRuntime(NexusAdaptiveRuntimeV9):

    def __init__(self):
        self.RELIABILITY_THRESHOLD = 0.5
        self.CONFIDENCE_THRESHOLD = 0.5

        self.reliability_data = {
            "PROCESS": {
                "successes": 9,
                "failures": 1
            },
            "THREAD": {
                "successes": 10,
                "failures": 0
            },
            "SEQUENTIAL": {
                "successes": 10,
                "failures": 0
            }
        }

    def _reliability_score(self, backend):
        data = self.reliability_data[backend]

        total = (
            data["successes"]
            + data["failures"]
        )

        return data["successes"] / total

    def _confidence_score(self, backend):
        data = self.reliability_data[backend]

        total = (
            data["successes"]
            + data["failures"]
        )

        return {
            "reliability":
                data["successes"] / total,

            "samples":
                total,

            "confidence":
                min(total / 10, 1.0)
        }


class FakeLearning:

    def decide(self, history, task_type):

        best = min(
            history,
            key=lambda b:
            history[b]["average_time"]
        )

        return {
            "mode": "EXPLOIT",
            "backend": best,
            "reason": "performance",
            "confidence": 1.0
        }


runtime = FakeRuntime()

runtime.learning = FakeLearning()


# ==========================================
# PERFORMANCE HISTORY
# ==========================================

history = {
    "PROCESS": {
        "average_time": 0.01,
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


print("=== ADAPTIVE RECOVERY TEST ===")
print()


# ==========================================
# PHASE 1
# PROCESS قوي وموثوق
# ==========================================

selected_1, _ = runtime._choose_backend(
    history,
    "CPU"
)

print("PHASE 1")
print("PROCESS RELIABILITY:",
      runtime._reliability_score("PROCESS"))

print("SELECTED:",
      selected_1["backend"])


# ==========================================
# PHASE 2
# PROCESS يفشل
#
# 9 successes + 11 failures
# = 45% reliability
# ==========================================

runtime.reliability_data["PROCESS"] = {
    "successes": 9,
    "failures": 11
}


selected_2, _ = runtime._choose_backend(
    history,
    "CPU"
)

print()
print("PHASE 2")
print("PROCESS RELIABILITY:",
      runtime._reliability_score("PROCESS"))

print("PROCESS CONFIDENCE:",
      runtime._confidence_score("PROCESS")["confidence"])

print("SELECTED:",
      selected_2["backend"])


# ==========================================
# PHASE 3
# PROCESS يتعافى
#
# 20 successes + 11 failures
# = 64.5% reliability
# ==========================================

runtime.reliability_data["PROCESS"] = {
    "successes": 20,
    "failures": 11
}


selected_3, _ = runtime._choose_backend(
    history,
    "CPU"
)

print()
print("PHASE 3")
print("PROCESS RELIABILITY:",
      runtime._reliability_score("PROCESS"))

print("PROCESS CONFIDENCE:",
      runtime._confidence_score("PROCESS")["confidence"])

print("SELECTED:",
      selected_3["backend"])


# ==========================================
# VALIDATION
# ==========================================

phase_1_correct = (
    selected_1["backend"] == "PROCESS"
)

phase_2_rejected = (
    selected_2["backend"] != "PROCESS"
)

phase_3_recovered = (
    selected_3["backend"] == "PROCESS"
)


print()
print("=== VALIDATION ===")

print(
    "PHASE 1 PROCESS SELECTED:",
    phase_1_correct
)

print(
    "PHASE 2 PROCESS REJECTED:",
    phase_2_rejected
)

print(
    "PHASE 3 PROCESS RECOVERED:",
    phase_3_recovered
)


passed = (
    phase_1_correct
    and phase_2_rejected
    and phase_3_recovered
)


print()
print("PASS:", passed)
