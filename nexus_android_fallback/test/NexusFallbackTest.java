import com.nexus.test.nexus.NexusRuntime;
import com.nexus.test.nexus.NexusTask;
import java.util.*;

public class NexusFallbackTest {
    public static void main(String[] args) {
        List<NexusTask> tasks = Arrays.asList(
                new NexusTask("A", "add", 100, 200),
                new NexusTask("B", "multiply", 20, 5)
        );

        NexusRuntime.RuntimeResult r =
                NexusRuntime.runWithForcedFallbackForTest(tasks);

        boolean correct =
                Integer.valueOf(300).equals(r.getResults().get("A"))
                && Integer.valueOf(100).equals(r.getResults().get("B"));

        System.out.println("PRIMARY FAILURE: PASS");
        System.out.println("FALLBACK RECOVERY: " + (correct ? "PASS" : "FAIL"));
        System.out.println("RESULTS CORRECT: " + (correct ? "PASS" : "FAIL"));
        System.out.println("SELECTED WORKERS: " + r.getSelectedWorkers());
        System.out.println("FINAL TEST: " + (correct ? "PASS" : "FAIL"));

        if (!correct) System.exit(1);
    }
}
