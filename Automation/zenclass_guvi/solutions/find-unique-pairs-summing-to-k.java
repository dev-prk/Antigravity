import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        int n = Integer.parseInt(br.readLine().trim());
        
        if (n <= 0) {
            System.out.println(-1);
            return;
        }
        
        String[] tokens = br.readLine().trim().split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(tokens[i]);
        }
        
        int k = Integer.parseInt(br.readLine().trim());
        
        // Use a set to store unique pairs
        Set<String> pairs = new LinkedHashSet<>();
        
        // Use a set to track seen elements
        Set<Integer> seen = new HashSet<>();
        
        for (int num : arr) {
            int complement = k - num;
            if (seen.contains(complement)) {
                // Store pair in sorted order
                int first = Math.min(num, complement);
                int second = Math.max(num, complement);
                pairs.add("(" + first + "," + second + ")");
            }
            seen.add(num);
        }
        
        if (pairs.isEmpty()) {
            System.out.println(-1);
        } else {
            for (String pair : pairs) {
                System.out.println(pair);
            }
        }
    }
}
