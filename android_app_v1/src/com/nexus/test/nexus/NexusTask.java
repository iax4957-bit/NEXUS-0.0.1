package com.nexus.test.nexus;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class NexusTask {

    private final String taskId;
    private final String operation;
    private final Object[] args;
    private final List<String> dependencies;
    private final String cacheKey;

    public NexusTask(
            String taskId,
            String operation,
            Object[] args,
            List<String> dependencies,
            String cacheKey
    ) {
        this.taskId = taskId;
        this.operation = operation;
        this.args = args;
        this.dependencies = new ArrayList<>(dependencies);
        this.cacheKey = cacheKey;
    }

    public NexusTask(
            String taskId,
            String operation,
            Object... args
    ) {
        this(
                taskId,
                operation,
                args,
                Collections.<String>emptyList(),
                ""
        );
    }

    public String getTaskId() {
        return taskId;
    }

    public String getOperation() {
        return operation;
    }

    public Object[] getArgs() {
        return args;
    }

    public List<String> getDependencies() {
        return Collections.unmodifiableList(dependencies);
    }

    public String getCacheKey() {
        return cacheKey;
    }
}