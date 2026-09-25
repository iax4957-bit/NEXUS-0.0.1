package com.nexus.test.nexus;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class NexusExecutor {

    private static volatile boolean FAIL_NEXT_JOB_FOR_TEST = false;

    public static void failNextJobForTest() {
        FAIL_NEXT_JOB_FOR_TEST = true;
    }


    public static Object executeJob(NexusTask task) {

        if (FAIL_NEXT_JOB_FOR_TEST) {
            FAIL_NEXT_JOB_FOR_TEST = false;
            throw new RuntimeException("FORCED_PRIMARY_FAILURE_FOR_TEST");
        }

        String operation = task.getOperation();
        Object[] args = task.getArgs();

        switch (operation) {

            case "add":
                return addValues(args);

            case "multiply":
                return multiplyValues(args);

            case "cpu":
                return cpuWork(args);

            case "collision_check":
                return collisionCheck(args);

            default:
                throw new IllegalArgumentException(
                        "Unknown operation: " + operation
                );
        }
    }

    private static int addValues(Object[] args) {

        if (args.length != 2) {
            throw new IllegalArgumentException(
                    "ADD requires 2 arguments"
            );
        }

        int a = ((Number) args[0]).intValue();
        int b = ((Number) args[1]).intValue();

        return a + b;
    }

    private static int multiplyValues(Object[] args) {

        if (args.length != 2) {
            throw new IllegalArgumentException(
                    "MULTIPLY requires 2 arguments"
            );
        }

        int a = ((Number) args[0]).intValue();
        int b = ((Number) args[1]).intValue();

        return a * b;
    }

    private static long cpuWork(Object[] args) {

        if (args.length < 1) {
            throw new IllegalArgumentException(
                    "CPU requires at least 1 argument"
            );
        }

        int value =
                ((Number) args[0]).intValue();

        int rounds = 80000;

        if (args.length >= 2) {
            rounds =
                    ((Number) args[1]).intValue();
        }

        long x = value + 1L;

        for (int i = 0; i < rounds; i++) {

            x =
                    (x * 1664525L
                            + 1013904223L
                            + i)
                            & 0xFFFFFFFFL;
        }

        return x;
    }

    /*
     * ========================================================
     * NEXUS PHYSICS
     * ========================================================
     *
     * Checks collision between:
     *
     *     circular ball
     *
     * and
     *
     *     rectangular block
     *
     * Arguments:
     *
     * 0 = ballX
     * 1 = ballY
     * 2 = ballRadius
     * 3 = blockX
     * 4 = blockY
     * 5 = blockWidth
     * 6 = blockHeight
     *
     * Returns:
     *
     * true  = collision
     * false = no collision
     */

    private static boolean collisionCheck(
            Object[] args
    ) {

        if (args.length != 7) {

            throw new IllegalArgumentException(
                    "COLLISION_CHECK requires 7 arguments"
            );
        }

        double ballX =
                ((Number) args[0]).doubleValue();

        double ballY =
                ((Number) args[1]).doubleValue();

        double radius =
                ((Number) args[2]).doubleValue();

        double blockX =
                ((Number) args[3]).doubleValue();

        double blockY =
                ((Number) args[4]).doubleValue();

        double blockWidth =
                ((Number) args[5]).doubleValue();

        double blockHeight =
                ((Number) args[6]).doubleValue();

        double closestX =
                clamp(
                        ballX,
                        blockX,
                        blockX + blockWidth
                );

        double closestY =
                clamp(
                        ballY,
                        blockY,
                        blockY + blockHeight
                );

        double dx =
                ballX - closestX;

        double dy =
                ballY - closestY;

        double distanceSquared =
                dx * dx + dy * dy;

        return distanceSquared <= radius * radius;
    }

    private static double clamp(
            double value,
            double minimum,
            double maximum
    ) {

        return Math.max(
                minimum,
                Math.min(
                        value,
                        maximum
                )
        );
    }

    public static Map<String, Object> executeThreads(
            List<NexusTask> tasks,
            int workers
    ) {

        Map<String, Object> results =
                new HashMap<>();

        if (tasks == null || tasks.isEmpty()) {
            return results;
        }

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

            Map<String, Future<Object>> futures =
                    new HashMap<>();

            for (NexusTask task : tasks) {

                Callable<Object> job =
                        () -> executeJob(task);

                futures.put(
                        task.getTaskId(),
                        executor.submit(job)
                );
            }

            for (NexusTask task : tasks) {

                Future<Object> future =
                        futures.get(
                                task.getTaskId()
                        );

                results.put(
                        task.getTaskId(),
                        future.get()
                );
            }

            return results;

        } catch (Exception e) {

            throw new RuntimeException(
                    "NEXUS execution failed",
                    e
            );

        } finally {

            executor.shutdown();
        }
    }
}