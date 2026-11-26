import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            return;
        }
        int n = Integer.parseInt(line.trim());
        
        List<Task> tasks = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            line = br.readLine();
            if (line == null) break;
            String[] parts = line.trim().split("\\s+");
            String taskId = parts[0];
            int priority = Integer.parseInt(parts[1]);
            tasks.add(new Task(taskId, priority, i));
        }
        
        tasks.sort((a, b) -> {
            if (b.priority != a.priority) {
                return Integer.compare(b.priority, a.priority);
            }
            return Integer.compare(a.index, b.index);
        });
        
        StringBuilder sb = new StringBuilder();
        for (Task t : tasks) {
            sb.append(t.taskId).append('\n');
        }
        System.out.print(sb.toString());
    }
    
    static class Task {
        String taskId;
        int priority;
        int index;
        
        Task(String taskId, int priority, int index) {
            this.taskId = taskId;
            this.priority = priority;
            this.index = index;
        }
    }
}
