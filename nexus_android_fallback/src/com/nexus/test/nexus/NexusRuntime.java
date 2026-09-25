package com.nexus.test.nexus;

import java.util.List;
import java.util.Map;

public class NexusRuntime {

    public static class RuntimeResult {

        private final Map<String, Object> results;
        private final NexusAdaptiveRuntime.SelectionResult selection;
        private final long executionTimeNanos;

        public RuntimeResult(
                Map<String, Object> results,
                NexusAdaptiveRuntime.SelectionResult selection,
                long executionTimeNanos
        ) {
            this.results = results;

            this.selection = selection;

            this.executionTimeNanos =
                    executionTimeNanos;
        }

        public Map<String, Object> getResults() {
            return results;
        }

        public NexusAdaptiveRuntime.SelectionResult getSelection() {
            return selection;
        }

        public long getExecutionTimeNanos() {
            return executionTimeNanos;
        }

        public double getExecutionTimeMillis() {

            return executionTimeNanos
                    / 1_000_000.0;
        }

        public int getSelectedWorkers() {

            return selection
                    .getSelectedWorkers();
        }

        public boolean isMemoryHit() {

            return selection
                    .isMemoryHit();
        }

        public String getWorkloadSignature() {

            return selection
                    .getWorkloadSignature();
        }

        public String getReport() {

            StringBuilder report =
                    new StringBuilder();

            report.append(
                    "NEXUS RUNTIME\n"
            );

            report.append(
                    "==============================\n\n"
            );

            report.append(
                    selection.getReport()
            );

            report.append(
                    "\n\n"
            );

            report.append(
                    "RUNTIME EXECUTION\n"
            );

            report.append(
                    "------------------------------\n"
            );

            report.append(
                    "SELECTED WORKERS = "
            );

            report.append(
                    getSelectedWorkers()
            );

            report.append(
                    "\n"
            );

            report.append(
                    "MEMORY = "
            );

            report.append(
                    isMemoryHit()
                            ? "HIT"
                            : "MISS"
            );

            report.append(
                    "\n"
            );

            report.append(
                    "EXECUTION TIME = "
            );

            report.append(
                    String.format(
                            java.util.Locale.US,
                            "%.2f ms",
                            getExecutionTimeMillis()
                    )
            );

            report.append(
                    "\n\n"
            );

            report.append(
                    "RESULTS\n"
            );

            report.append(
                    "------------------------------\n"
            );

            for (
                    Map.Entry<String, Object> entry
                    : results.entrySet()
            ) {

                report.append(
                        entry.getKey()
                );

                report.append(
                        " = "
                );

                report.append(
                        entry.getValue()
                );

                report.append(
                        "\n"
                );
            }

            return report.toString();
        }
    }

    public static RuntimeResult run(
            List<NexusTask> tasks
    ) {

        if (
                tasks == null
                || tasks.isEmpty()
        ) {

            throw new IllegalArgumentException(
                    "NEXUS Runtime requires at least one task"
            );
        }

        /*
         * Step 1:
         *
         * Let NEXUS determine the best worker count.
         */

        NexusAdaptiveRuntime.SelectionResult selection =
                NexusAdaptiveRuntime.selectWorkers(
                        tasks
                );

        /*
         * Step 2:
         *
         * Execute the REAL workload using the
         * selected worker count.
         */

        long start =
                System.nanoTime();

        try {

            Map<String, Object> results =
                    NexusCore.runParallel(
                            tasks,
                            selection.getSelectedWorkers()
                    );

            long end =
                    System.nanoTime();

            long executionTimeNanos =
                    end - start;

            /*
             * Step 3:
             *
             * The workload actually completed.
             *
             * NOW, and only now, record the execution
             * as a successful learning observation.
             */

            NexusAdaptiveRuntime.recordExecutionSuccess(
                    selection,
                    executionTimeNanos
                            / 1_000_000.0
            );

            /*
             * Step 4:
             *
             * Return everything needed by the caller.
             */

            return new RuntimeResult(
                    results,
                    selection,
                    executionTimeNanos
            );

        } catch (Throwable primaryError) {

            // Primary PARALLEL path failed. Record the failure, then recover.
            NexusAdaptiveRuntime.recordExecutionFailure(selection);

            long fallbackStart = System.nanoTime();

            try {
                // Fallback path: dependency-aware SEQUENTIAL execution.
                Map<String, Object> fallbackResults =
                        NexusCore.run(tasks);

                long fallbackEnd = System.nanoTime();
                long fallbackTime = fallbackEnd - fallbackStart;

                NexusAdaptiveRuntime.recordExecutionSuccess(
                        selection,
                        fallbackTime / 1_000_000.0
                );

                return new RuntimeResult(
                        fallbackResults,
                        selection,
                        fallbackTime
                );

            } catch (Throwable fallbackError) {

                RuntimeException combined =
                        new RuntimeException(
                                "NEXUS Runtime primary and fallback execution failed",
                                primaryError
                        );

                combined.addSuppressed(fallbackError);
                throw combined;
            }
        }
    }

    public static RuntimeResult runWithForcedFallbackForTest(
            List<NexusTask> tasks
    ) {
        NexusAdaptiveRuntime.SelectionResult selection =
                NexusAdaptiveRuntime.selectWorkers(tasks);

        NexusExecutor.failNextJobForTest();

        long start = System.nanoTime();
        try {
            Map<String, Object> results =
                    NexusCore.runParallel(
                            tasks,
                            selection.getSelectedWorkers()
                    );

            long end = System.nanoTime();
            return new RuntimeResult(
                    results,
                    selection,
                    end - start
            );

        } catch (Throwable primaryError) {
            NexusAdaptiveRuntime.recordExecutionFailure(selection);

            long fallbackStart = System.nanoTime();
            Map<String, Object> fallbackResults =
                    NexusCore.run(tasks);
            long fallbackEnd = System.nanoTime();

            NexusAdaptiveRuntime.recordExecutionSuccess(
                    selection,
                    (fallbackEnd - fallbackStart) / 1_000_000.0
            );

            return new RuntimeResult(
                    fallbackResults,
                    selection,
                    fallbackEnd - fallbackStart
            );
        }
    }

    public static Map<String, Object> runSimple(
            List<NexusTask> tasks
    ) {

        return run(
                tasks
        ).getResults();
    }

    public static int selectWorkers(
            List<NexusTask> tasks
    ) {

        return NexusAdaptiveRuntime
                .selectWorkers(
                        tasks
                )
                .getSelectedWorkers();
    }

    public static String inspect(
            List<NexusTask> tasks
    ) {

        return NexusAdaptiveRuntime
                .selectWorkers(
                        tasks
                )
                .getReport();
    }
}