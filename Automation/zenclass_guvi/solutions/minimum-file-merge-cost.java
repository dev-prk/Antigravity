import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nStr = br.readLine();
        if (nStr == null || nStr.isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(nStr.trim());
        if (n <= 1) {
            System.out.println(0);
            return;
        }
        
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            System.out.println(0);
            return;
        }
        
        String[] parts = line.trim().split("\\s+");
        PriorityQueue<Long> pq = new PriorityQueue<>();
        for (int i = 0; i < n && i < parts.length; i++) {
            long val = Long.parseLong(parts[i].trim());
            if (val > 0) {
                pq.offer(val);
            }
        }
        
        long totalCost = 0;
        while (pq.size() > 1) {
            long a = pq.poll();
            long b = pq.poll();
            long sum = a + b;
            totalCost += sum;
            pq.offer(sum);
        }
        
        System.out.println(totalCost);
    }
}
