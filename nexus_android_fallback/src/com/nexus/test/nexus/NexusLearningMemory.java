package com.nexus.test.nexus;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class NexusLearningMemory {

    public static class LearningEntry {

        private final String signature;

        private int selectedWorkers;
        private double medianTime;

        private int samples;
        private int successes;
        private int failures;

        public LearningEntry(
                String signature,
                int selectedWorkers,
                double medianTime
        ) {

            this.signature = signature;

            this.selectedWorkers =
                    selectedWorkers;

            this.medianTime =
                    medianTime;

            this.samples = 1;
            this.successes = 1;
            this.failures = 0;
        }

        public synchronized String getSignature() {
            return signature;
        }

        public synchronized int getSelectedWorkers() {
            return selectedWorkers;
        }

        public synchronized double getMedianTime() {
            return medianTime;
        }

        public synchronized int getSamples() {
            return samples;
        }

        public synchronized int getSuccesses() {
            return successes;
        }

        public synchronized int getFailures() {
            return failures;
        }

        public synchronized double getReliability() {

            int total =
                    successes + failures;

            if (total == 0) {
                return 0.0;
            }

            return (double) successes / total;
        }

        public synchronized void recordSuccess(
                int workers,
                double time
        ) {

            samples++;
            successes++;

            selectedWorkers =
                    workers;

            /*
             * Keep the latest measured performance
             * for the learned choice.
             */
            medianTime =
                    time;
        }

        public synchronized void recordFailure() {

            samples++;
            failures++;
        }
    }

    private final ConcurrentMap<String, LearningEntry> memory =
            new ConcurrentHashMap<>();

    public LearningEntry get(
            String signature
    ) {

        if (signature == null) {
            return null;
        }

        return memory.get(
                signature
        );
    }

    public void put(
            String signature,
            int selectedWorkers,
            double medianTime
    ) {

        if (signature == null) {
            throw new IllegalArgumentException(
                    "Learning signature cannot be null"
            );
        }

        if (selectedWorkers < 1) {
            throw new IllegalArgumentException(
                    "Selected workers must be >= 1"
            );
        }

        memory.put(
                signature,
                new LearningEntry(
                        signature,
                        selectedWorkers,
                        medianTime
                )
        );
    }

    public boolean contains(
            String signature
    ) {

        return signature != null
                && memory.containsKey(
                        signature
                );
    }

    public boolean hasChoice(
            String signature
    ) {

        return contains(
                signature
        );
    }

    public boolean hasReliableChoice(
            String signature
    ) {

        LearningEntry entry =
                get(signature);

        if (entry == null) {
            return false;
        }

        return entry.getSamples() >= 3
                && entry.getReliability() >= 0.66;
    }

    public void recordSuccess(
            String signature,
            int workers,
            double time
    ) {

        if (signature == null) {
            return;
        }

        LearningEntry entry =
                memory.get(
                        signature
                );

        if (entry == null) {

            put(
                    signature,
                    workers,
                    time
            );

            return;
        }

        entry.recordSuccess(
                workers,
                time
        );
    }

    public void recordFailure(
            String signature
    ) {

        if (signature == null) {
            return;
        }

        LearningEntry entry =
                memory.get(
                        signature
                );

        if (entry != null) {

            entry.recordFailure();
        }
    }

    public int size() {

        return memory.size();
    }

    public void clear() {

        memory.clear();
    }
}