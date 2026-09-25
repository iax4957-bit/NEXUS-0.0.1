package com.nexus.test.nexus;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class NexusWorkGraph {

    private final Map<String, NexusTask> tasks =
            new HashMap<>();

    public void add(NexusTask task) {

        if (task == null) {
            throw new IllegalArgumentException(
                    "NEXUS cannot add a null task"
            );
        }

        if (tasks.containsKey(task.getTaskId())) {

            throw new IllegalArgumentException(
                    "Duplicate task: "
                            + task.getTaskId()
            );
        }

        tasks.put(
                task.getTaskId(),
                task
        );
    }

    public boolean validate() {

        /*
         * Validate explicit dependencies
         * and dependencies represented by ResultRef.
         */

        for (NexusTask task : tasks.values()) {

            for (
                    String dependency
                    : getAllDependencies(task)
            ) {

                if (!tasks.containsKey(dependency)) {

                    throw new IllegalArgumentException(
                            "Missing dependency: "
                                    + dependency
                                    + " required by "
                                    + task.getTaskId()
                    );
                }
            }
        }

        Set<String> visiting =
                new HashSet<>();

        Set<String> visited =
                new HashSet<>();

        for (String taskId : tasks.keySet()) {

            visit(
                    taskId,
                    visiting,
                    visited
            );
        }

        return true;
    }

    private void visit(
            String taskId,
            Set<String> visiting,
            Set<String> visited
    ) {

        if (visiting.contains(taskId)) {

            throw new IllegalArgumentException(
                    "Cycle detected: "
                            + taskId
            );
        }

        if (visited.contains(taskId)) {
            return;
        }

        visiting.add(taskId);

        NexusTask task =
                tasks.get(taskId);

        if (task == null) {

            throw new IllegalStateException(
                    "Task not found: "
                            + taskId
            );
        }

        for (
                String dependency
                : getAllDependencies(task)
        ) {

            visit(
                    dependency,
                    visiting,
                    visited
            );
        }

        visiting.remove(taskId);

        visited.add(taskId);
    }

    public List<NexusTask> ready(
            Set<String> completed
    ) {

        List<NexusTask> result =
                new ArrayList<>();

        for (
                NexusTask task
                : tasks.values()
        ) {

            /*
             * Already completed tasks
             * are never returned.
             */

            if (
                    completed.contains(
                            task.getTaskId()
                    )
            ) {

                continue;
            }

            boolean ready = true;

            /*
             * IMPORTANT:
             *
             * We now check BOTH:
             *
             * 1. Explicit dependencies
             * 2. ResultRef dependencies
             */

            for (
                    String dependency
                    : getAllDependencies(task)
            ) {

                if (
                        !completed.contains(
                                dependency
                        )
                ) {

                    ready = false;

                    break;
                }
            }

            if (ready) {

                result.add(task);
            }
        }

        return result;
    }

    /**
     * Returns all dependencies of a task.
     *
     * Dependencies can come from:
     *
     * 1. NexusTask.dependencies
     *
     * 2. NexusCore.ResultRef inside task arguments
     */
    private Set<String> getAllDependencies(
            NexusTask task
    ) {

        Set<String> dependencies =
                new HashSet<>();

        /*
         * Explicit dependencies.
         */

        dependencies.addAll(
                task.getDependencies()
        );

        /*
         * Dependencies encoded through ResultRef.
         */

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

                    NexusCore.ResultRef reference =
                            (NexusCore.ResultRef) arg;

                    dependencies.add(
                            reference.getTaskId()
                    );
                }
            }
        }

        return dependencies;
    }

    public int size() {

        return tasks.size();
    }
}