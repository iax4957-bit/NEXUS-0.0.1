"""
NEXUS Runtime V1
Application-facing runtime layer for NEXUS 0.0.1
"""

from nexus_unified_v2 import NexusUnifiedV2


class NexusRuntimeV1:
    """
    Stable application-facing interface.

    Applications should communicate with this class
    instead of directly depending on the internal engine.
    """

    VERSION = "NEXUS RUNTIME V1"

    def __init__(self, max_workers=4):
        self.engine = NexusUnifiedV2(
            max_workers=max_workers,
            exploration_repeats=2,
        )

    def add_task(
        self,
        task_id,
        operation,
        args=(),
        dependencies=(),
    ):
        self.engine.add_task(
            task_id,
            operation,
            args,
            dependencies,
        )

    def run(self):
        return self.engine.run()

    def get_results(self):
        return dict(self.engine.results)


    def execute(self, tasks):
        """
        Execute an application request.

        tasks must be an iterable of dictionaries:
            {
                "id": "...",
                "operation": "...",
                "args": (...),
                "dependencies": (...),
            }

        Returns results and runtime statistics.
        """
        for task in tasks:
            self.add_task(
                task["id"],
                task["operation"],
                task.get("args", ()),
                task.get("dependencies", ()),
            )

        results = self.run()

        return {
            "results": results,
            "stats": self.stats(),
        }


    def handle_request(self, request):
        """
        Application-facing request handler.

        Each request starts with a fresh engine state so
        tasks and results from previous requests cannot leak.
        """

        self.engine = NexusUnifiedV2(
            max_workers=self.engine.max_workers,
            exploration_repeats=2,
        )

        """
        Application-facing request handler.

        Expected request:
            {
                "tasks": [
                    {
                        "id": "...",
                        "operation": "...",
                        "args": (...),
                        "dependencies": (...),
                    }
                ]
            }
        """

        if not isinstance(request, dict):
            raise TypeError("request must be a dictionary")

        tasks = request.get("tasks")

        if not isinstance(tasks, list):
            raise TypeError("request['tasks'] must be a list")

        for task in tasks:
            if not isinstance(task, dict):
                raise TypeError("each task must be a dictionary")

            if "id" not in task:
                raise ValueError("task missing 'id'")

            if "operation" not in task:
                raise ValueError("task missing 'operation'")

            args = task.get("args", [])

            if isinstance(args, list):
                converted_args = []

                for arg in args:
                    if isinstance(arg, list) and len(arg) == 2 and arg[0] == "$":
                        converted_args.append(("$", arg[1]))
                    else:
                        converted_args.append(arg)

                task["args"] = tuple(converted_args)

        return self.execute(tasks)

    def stats(self):
        return {
            "version": self.VERSION,
            "executions": self.engine.execution_count,
            "cache_hits": self.engine.cache_hits,
            "batches": self.engine.batch_count,
            "cache_size": len(self.engine.cache),
            "results": len(self.engine.results),
        }
