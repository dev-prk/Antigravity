import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(line.trim());
        if (n == 0) {
            System.out.println(0);
            return;
        }
        Activity[] activities = new Activity[n];
        for (int i = 0; i < n; i++) {
            line = br.readLine();
            if (line == null || line.isEmpty()) {
                System.out.println(0);
                return;
            }
            String[] parts = line.trim().split("\\s+");
            int s = Integer.parseInt(parts[0]);
            int e = Integer.parseInt(parts[1]);
            activities[i] = new Activity(s, e);
        }
        Arrays.sort(activities, (a, b) -> {
            if (a.end != b.end) {
                return Integer.compare(a.end, b.end);
            }
            return Integer.compare(a.start, b.start);
        });
        int count = 0;
        int lastEnd = Integer.MIN_VALUE;
        for (Activity act : activities) {
            if (act.start >= lastEnd) {
                count++;
                lastEnd = act.end;
            }
        }
        System.out.println(count);
    }
    
    static class Activity {
        int start;
        int end;
        Activity(int s, int e) {
            this.start = s;
            this.end = e;
        }
    }
}
