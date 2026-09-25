"""
NEXUS App API V1
Application bridge for NEXUS 0.0.1
"""

from nexus_runtime_v1 import NexusRuntimeV1


class NexusAppAPIv1:
    VERSION = "NEXUS APP API V1"

    def __init__(self, max_workers=4):
        self.runtime = NexusRuntimeV1(
            max_workers=max_workers
        )

    def run(self, request):
        if not isinstance(request, dict):
            raise TypeError("request must be a dictionary")

        response = self.runtime.handle_request(request)

        return {
            "version": self.VERSION,
            "results": response["results"],
            "stats": response["stats"],
        }
