import tempfile

from nexus_adaptive_runtime_v13 import NexusAdaptiveRuntimeV13


class TestRuntime(NexusAdaptiveRuntimeV13):

    def __init__(self, memory_file, reliability_file):
        super().__init__(
            workers=2,
            batch_size=3,
            exploration_rate=0.0,
            memory_file=memory_file,
            reliability_file=reliability_file
        )


memory_file = tempfile.mktemp(
    prefix="nexus_v13_memory_",
    suffix=".json"
)

reliability_file = tempfile.mktemp(
    prefix="nexus_v13_reliability_",
    suffix=".json"
)

runtime = TestRuntime(
    memory_file,
    reliability_file
)

history = {
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

print("=== NEXUS V13 EXPLORATION TEST ===")
print()

exploit = runtime.choose_with_exploration(
    history,
    "CPU",
    force_exploration=False
)

print("EXPLOIT MODE:", exploit["mode"])
print("EXPLOIT BACKEND:", exploit["backend"])
print("EXPLOIT PREFERRED:", exploit["preferred_backend"])

exploit_ok = (
    exploit["mode"] == "EXPLOIT"
    and exploit["backend"] == "PROCESS"
    and exploit["preferred_backend"] == "PROCESS"
)

print("EXPLOIT TEST:", exploit_ok)
print()

explore = runtime.choose_with_exploration(
    history,
    "CPU",
    force_exploration=True
)

print("EXPLORE MODE:", explore["mode"])
print("EXPLORE BACKEND:", explore["backend"])
print("EXPLORE PREFERRED:", explore["preferred_backend"])

explore_ok = (
    explore["mode"] == "EXPLORE"
    and explore["exploration"] is True
    and explore["preferred_backend"] == "PROCESS"
    and explore["backend"] != explore["preferred_backend"]
)

print("EXPLORE TEST:", explore_ok)
print()

passed = exploit_ok and explore_ok

print("FINAL PASS:", passed)
