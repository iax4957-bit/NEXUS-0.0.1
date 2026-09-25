package com.nexus.test.nexus;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class NexusCore {

    public static class ResultRef {

        private final String taskId;

        public ResultRef(String taskId) {
            this.taskId = taskId;
        }

        public String getTaskId() {
            return taskId;
        }
    }

    /*
     * =========================================================
     * SEQUENTIAL EXECUTION
     * =========================================================
     */

    public static Map<String, Object> run(
            List<NexusTask> tasks
    ) {

        if (tasks == null || tasks.isEmpty()) {
            return new HashMap<>();
        }

        NexusWorkGraph graph =
                new NexusWorkGraph();

        for (NexusTask task : tasks) {
            graph.add(task);
        }

        graph.validate();

        Set<String> completed =
                new HashSet<>();

        Map<String, Object> results =
                new HashMap<>();

        while (
                completed.size()
                        < graph.size()
        ) {

            List<NexusTask> readyTasks =
                    graph.ready(completed);

            if (readyTasks.isEmpty()) {

                throw new IllegalStateException(
                        "NEXUS cannot continue: "
                                + "no ready tasks remain."
                );
            }

            for (NexusTask task : readyTasks) {

                Object[] resolvedArgs =
                        resolveArguments(
                                task,
                                results
                        );

                NexusTask executableTask =
                        new NexusTask(
                                task.getTaskId(),
                                task.getOperation(),
                                resolvedArgs
                        );

                try {

                    Object result =
                            NexusExecutor.executeJob(
                                    executableTask
                            );

                    results.put(
                            task.getTaskId(),
                            result
                    );

                    completed.add(
                            task.getTaskId()
                    );

                } catch (Throwable error) {

                    throw new RuntimeException(
                            "NEXUS task failed: "
                                    + task.getTaskId()
                                    + " | operation="
                                    + task.getOperation(),
                            error
                    );
                }
            }
        }

        return results;
    }

    /*
     * =========================================================
     * PARALLEL EXECUTION
     * =========================================================
     */

    public static Map<String, Object> runParallel(
            List<NexusTask> tasks,
            int workers
    ) {

        if (tasks == null || tasks.isEmpty()) {
            return new HashMap<>();
        }

        NexusWorkGraph graph =
                new NexusWorkGraph();

        for (NexusTask task : tasks) {
            graph.add(task);
        }

        graph.validate();

        Set<String> completed =
                new HashSet<>();

        Map<String, Object> results =
                new HashMap<>();

        workers =
                Math.max(
                        1,
                        Math.min(
                                workers,
                                tasks.size()
                        )
                );

        ExecutorService executor =
                Executors.newFixedThreadPool(
                        workers
                );

        try {

            while (
                    completed.size()
                            < graph.size()
            ) {

                List<NexusTask> readyTasks =
                        graph.ready(completed);

                if (readyTasks.isEmpty()) {

                    throw new IllegalStateException(
                            "NEXUS cannot continue: "
                                    + "no ready tasks remain."
                    );
                }

                /*
                 * -------------------------------------------------
                 * Prepare jobs for this dependency level.
                 * -------------------------------------------------
                 */

                List<NexusTask> scheduledTasks =
                        new ArrayList<>();

                List<Callable<Object>> jobs =
                        new ArrayList<>();

                for (
                        NexusTask task
                        : readyTasks
                ) {

                    Object[] resolvedArgs =
                            resolveArguments(
                                    task,
                                    results
                            );

                    NexusTask executableTask =
                            new NexusTask(
                                    task.getTaskId(),
                                    task.getOperation(),
                                    resolvedArgs
                            );

                    scheduledTasks.add(
                            task
                    );

                    jobs.add(
                            () ->
                                    NexusExecutor.executeJob(
                                            executableTask
                                    )
                    );
                }

                /*
                 * -------------------------------------------------
                 * Submit jobs.
                 * -------------------------------------------------
                 */

                List<Future<Object>> futures =
                        new ArrayList<>();

                for (
                        Callable<Object> job
                        : jobs
                ) {

                    futures.add(
                            executor.submit(job)
                    );
                }

                /*
                 * -------------------------------------------------
                 * Collect results.
                 * -------------------------------------------------
                 */

                for (
                        int i = 0;
                        i < futures.size();
                        i++
                ) {

                    Future<Object> future =
                            futures.get(i);

                    NexusTask task =
                            scheduledTasks.get(i);

                    try {

                        Object result =
                                future.get();

                        results.put(
                                task.getTaskId(),
                                result
                        );

                    } catch (ExecutionException error) {

                        Throwable cause =
                                error.getCause();

                        String causeMessage =
                                cause == null
                                        ? "unknown cause"
                                        : cause.getClass()
                                                .getSimpleName()
                                                + ": "
                                                + cause.getMessage();

                        throw new RuntimeException(
                                "NEXUS task failed: "
                                        + task.getTaskId()
                                        + " | operation="
                                        + task.getOperation()
                                        + " | cause="
                                        + causeMessage,
                                cause
                        );

                    } catch (InterruptedException error) {

                        Thread.currentThread()
                                .interrupt();

                        throw new RuntimeException(
                                "NEXUS interrupted while "
                                        + "waiting for task: "
                                        + task.getTaskId(),
                                error
                        );
                    }
                }

                /*
                 * -------------------------------------------------
                 * Mark this dependency level complete
                 * only after every result was collected.
                 * -------------------------------------------------
                 */

                for (
                        NexusTask task
                        : scheduledTasks
                ) {

                    completed.add(
                            task.getTaskId()
                    );
                }
            }

            return results;

        } catch (RuntimeException error) {

            throw error;

        } catch (Throwable error) {

            throw new RuntimeException(
                    "NEXUS parallel execution failed",
                    error
            );

        } finally {

            executor.shutdown();
        }
    }

    /*
     * =========================================================
     * ARGUMENT RESOLUTION
     * =========================================================
     */

    private static Object[] resolveArguments(
            NexusTask task,
            Map<String, Object> results
    ) {

        Object[] originalArgs =
                task.getArgs();

        Object[] resolvedArgs =
                new Object[
                        originalArgs.length
                ];

        for (
                int i = 0;
                i < originalArgs.length;
                i++
        ) {

            Object arg =
                    originalArgs[i];

            if (
                    arg instanceof ResultRef
            ) {

                ResultRef reference =
                        (ResultRef) arg;

                String referencedTaskId =
                        reference.getTaskId();

                if (
                        !results.containsKey(
                                referencedTaskId
                        )
                ) {

                    throw new IllegalStateException(
                            "Result not available for task: "
                                    + referencedTaskId
                                    + " required by "
                                    + task.getTaskId()
                    );
                }

                resolvedArgs[i] =
                        results.get(
                                referencedTaskId
                        );

            } else {

                resolvedArgs[i] =
                        arg;
            }
        }

        return resolvedArgs;
    }
}