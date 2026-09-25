class NexusTaskClassifierV1:

    SMALL_WORKLOAD = 10
    CPU_INTENSIVE_RATIO = 0.7
    IO_INTENSIVE_RATIO = 0.7

    def classify(
        self,
        workload_size,
        cpu_ratio=0.0,
        io_ratio=0.0
    ):

        workload_size = max(
            0,
            int(workload_size)
        )

        cpu_ratio = max(
            0.0,
            min(float(cpu_ratio), 1.0)
        )

        io_ratio = max(
            0.0,
            min(float(io_ratio), 1.0)
        )

        if workload_size <= self.SMALL_WORKLOAD:
            task_type = "SMALL"

        elif cpu_ratio >= self.CPU_INTENSIVE_RATIO:
            task_type = "CPU"

        elif io_ratio >= self.IO_INTENSIVE_RATIO:
            task_type = "IO"

        else:
            task_type = "MIXED"

        return {
            "task_type": task_type,
            "workload_size": workload_size,
            "cpu_ratio": cpu_ratio,
            "io_ratio": io_ratio
        }
