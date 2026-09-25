package com.nexus.test.nexus;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class NexusAdaptiveRuntime {

    private static final NexusLearningMemory MEMORY =
            new NexusLearningMemory();

    public static class SelectionResult {

        private final int selectedWorkers;
        private final int availableProcessors;
        private final int candidateWorkers;
        private final Map<Integer, Double> medianTimes;
        private final boolean memoryHit;
        private final String workloadSignature;

        public SelectionResult(
                int selectedWorkers,
                int availableProcessors,
                int candidateWorkers,
                Map<Integer, Double> medianTimes,
                boolean memoryHit,
                String workloadSignature
        ) {

            this.selectedWorkers =
                    selectedWorkers;

            this.availableProcessors =
                    availableProcessors;

            this.candidateWorkers =
                    candidateWorkers;

            this.medianTimes =
                    new LinkedHashMap<>(
                            medianTimes
                    );

            this.memoryHit =
                    memoryHit;

            this.workloadSignature =
                    workloadSignature;
        }

        public int getSelectedWorkers() {
            return selectedWorkers;
        }

        public int getAvailableProcessors() {
            return availableProcessors;
        }

        public int getCandidateWorkers() {
            return candidateWorkers;
        }

        public Map<Integer, Double> getMedianTimes() {
            return medianTimes;
        }

        public boolean isMemoryHit() {
            return memoryHit;
        }

        public String getWorkloadSignature() {
            return workloadSignature;
        }

        public String getReport() {

            StringBuilder report =
                    new StringBuilder();

            report.append(
                    "NEXUS ADAPTIVE WORKERS\n"
            );

            report.append(
                    "------------------------------\n"
            );

            report.append(
                    "AVAILABLE PROCESSORS = "
            );

            report.append(
                    availableProcessors
            );

            report.append("\n");

            report.append(
                    "CANDIDATE WORKERS = "
            );

            report.append(
                    candidateWorkers
            );

            report.append("\n\n");

            report.append(
                    "WORKLOAD SIGNATURE\n"
            );

            report.append(
                    "------------------------------\n"
            );

            report.append(
                    workloadSignature
            );

            report.append("\n\n");

            if (memoryHit) {

                NexusLearningMemory.LearningEntry entry =
                        MEMORY.get(
                                workloadSignature
                        );

                report.append(
                        "MEMORY = HIT\n"
                );

                report.append(
                        "------------------------------\n"
                );

                report.append(
                        "LEARNED WORKERS = "
                );

                report.append(
                        selectedWorkers
                );

                report.append("\n");

                if (entry != null) {

                    report.append(
                            "LEARNED MEDIAN = "
                    );

                    report.append(
                            String.format(
                                    Locale.US,
                                    "%.2f ms",
                                    entry.getMedianTime()
                            )
                    );

                    report.append("\n");

                    report.append(
                            "SAMPLES = "
                    );

                    report.append(
                            entry.getSamples()
                    );

                    report.append("\n");

                    report.append(
                            "SUCCESSFUL RUNS = "
                    );

                    report.append(
                            entry.getSuccesses()
                    );

                    report.append("\n");

                    report.append(
                            "FAILED RUNS = "
                    );

                    report.append(
                            entry.getFailures()
                    );

                    report.append("\n");

                    report.append(
                            "RELIABILITY = "
                    );

                    report.append(
                            String.format(
                                    Locale.US,
                                    "%.2f",
                                    entry.getReliability()
                            )
                    );

                    report.append("\n");
                }

                report.append("\n");

                report.append(
                        "SELECTION = MEMORY"
                );

                return report.toString();
            }

            report.append(
                    "MEMORY = MISS\n"
            );

            report.append(
                    "------------------------------\n"
            );

            report.append(
                    "MEASURED MEDIANS\n"
            );

            report.append(
                    "------------------------------\n"
            );

            for (
                    Map.Entry<Integer, Double> entry
                    : medianTimes.entrySet()
            ) {

                report.append(
                        entry.getKey()
                );

                report.append(
                        " WORKER"
                );

                if (entry.getKey() > 1) {
                    report.append("S");
                }

                report.append(
                        " = "
                );

                report.append(
                        String.format(
                                Locale.US,
                                "%.2f ms",
                                entry.getValue()
                        )
                );

                report.append("\n");
            }

            report.append("\n");

            report.append(
                    "SELECTED WORKERS = "
            );

            report.append(
                    selectedWorkers
            );

            report.append("\n");

            report.append(
                    "SELECTION = ADAPTIVE + LEARNING"
            );

            return report.toString();
        }
    }

    public static SelectionResult selectWorkers(
            List<NexusTask> tasks
    ) {

        if (
                tasks == null
                || tasks.isEmpty()
        ) {

            throw new IllegalArgumentException(
                    "NEXUS requires at least one task"
            );
        }

        int availableProcessors =
                Math.max(
                        1,
                        Runtime
                                .getRuntime()
                                .availableProcessors()
                );

        int candidateWorkers =
                Math.max(
                        1,
                        Math.min(
                                availableProcessors,
                                tasks.size()
                        )
                );

        String signature =
                buildWorkloadSignature(
                        tasks
                );

        /*
         * =====================================================
         * MEMORY HIT
         * =====================================================
         *
         * The previous execution already established that
         * this workload can use the learned worker count.
         *
         * Each subsequent selection is recorded as another
         * successful observation of the learned choice.
         */

        if (
                MEMORY.hasChoice(
                        signature
                )
        ) {

            NexusLearningMemory.LearningEntry entry =
                    MEMORY.get(
                            signature
                    );

            if (entry != null) {

                int learnedWorkers =
                        Math.max(
                                1,
                                Math.min(
                                        entry.getSelectedWorkers(),
                                        candidateWorkers
                                )
                        );

                /*
                 * Record another successful observation.
                 *
                 * We do not invent a new timing here.
                 * The previous learned timing remains the
                 * stored reference.
                 */

                MEMORY.recordSuccess(
                        signature,
                        learnedWorkers,
                        entry.getMedianTime()
                );

                NexusLearningMemory.LearningEntry updated =
                        MEMORY.get(
                                signature
                        );

                Map<Integer, Double> learnedTimes =
                        new LinkedHashMap<>();

                if (updated != null) {

                    learnedTimes.put(
                            updated.getSelectedWorkers(),
                            updated.getMedianTime()
                    );

                    return new SelectionResult(
                            updated.getSelectedWorkers(),
                            availableProcessors,
                            candidateWorkers,
                            learnedTimes,
                            true,
                            signature
                    );
                }
            }
        }

        /*
         * =====================================================
         * ADAPTIVE MEASUREMENT
         * =====================================================
         */

        Map<Integer, Double> medianTimes =
                new LinkedHashMap<>();

        int selectedWorkers = 1;

        double bestTime =
                Double.MAX_VALUE;

        int warmupRuns = 2;

        int measuredRuns = 3;

        for (
                int workers = 1;
                workers <= candidateWorkers;
                workers++
        ) {

            /*
             * Warmup.
             */

            for (
                    int i = 0;
                    i < warmupRuns;
                    i++
            ) {

                NexusCore.runParallel(
                        tasks,
                        workers
                );
            }

            /*
             * Measurements.
             */

            List<Double> measurements =
                    new ArrayList<>();

            for (
                    int i = 0;
                    i < measuredRuns;
                    i++
            ) {

                long start =
                        System.nanoTime();

                NexusCore.runParallel(
                        tasks,
                        workers
                );

                long end =
                        System.nanoTime();

                measurements.add(
                        (end - start)
                                / 1_000_000.0
                );
            }

            double median =
                    median(
                            measurements
                    );

            medianTimes.put(
                    workers,
                    median
            );

            if (
                    median < bestTime
            ) {

                bestTime =
                        median;

                selectedWorkers =
                        workers;
            }
        }

        /*
         * Store the first learned decision.
         */

        MEMORY.put(
                signature,
                selectedWorkers,
                bestTime
        );

        return new SelectionResult(
                selectedWorkers,
                availableProcessors,
                candidateWorkers,
                medianTimes,
                false,
                signature
        );
    }

    public static void recordExecutionSuccess(
            SelectionResult selection,
            double executionTimeMillis
    ) {
        if (selection == null) return;
        MEMORY.recordSuccess(
                selection.getWorkloadSignature(),
                selection.getSelectedWorkers(),
                executionTimeMillis
        );
    }

    public static void recordExecutionFailure(
            SelectionResult selection
    ) {
        if (selection == null) return;
        MEMORY.recordFailure(
                selection.getWorkloadSignature()
        );
    }

    private static String buildWorkloadSignature(
            List<NexusTask> tasks
    ) {

        StringBuilder signature =
                new StringBuilder();

        signature.append(
                "TASKS="
        );

        signature.append(
                tasks.size()
        );

        signature.append("|");

        for (
                NexusTask task
                : tasks
        ) {

            signature.append(
                    task.getOperation()
            );

            signature.append("(");

            Object[] args =
                    task.getArgs();

            if (args != null) {

                for (
                        Object arg
                        : args
                ) {

                    if (
                            arg instanceof
                            NexusCore.ResultRef
                    ) {

                        signature.append(
                                "RESULT_REF"
                        );

                    } else if (
                            arg instanceof Number
                    ) {

                        signature.append(
                                arg
                        );

                    } else {

                        signature.append(
                                String.valueOf(
                                        arg
                                )
                        );
                    }

                    signature.append(",");
                }
            }

            signature.append(
                    ");"
            );
        }

        return signature.toString();
    }

    private static double median(
            List<Double> values
    ) {

        if (
                values == null
                || values.isEmpty()
        ) {

            throw new IllegalArgumentException(
                    "Cannot calculate median of empty data"
            );
        }

        List<Double> sorted =
                new ArrayList<>(
                        values
                );

        Collections.sort(
                sorted
        );

        int middle =
                sorted.size() / 2;

        if (
                sorted.size() % 2 == 1
        ) {

            return sorted.get(
                    middle
            );
        }

        return (
                sorted.get(
                        middle - 1
                )
                +
                sorted.get(
                        middle
                )
        ) / 2.0;
    }
}