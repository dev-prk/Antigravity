import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        int n = Integer.parseInt(br.readLine().trim());
        
        int[] arr = new int[n];
        if (n > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int i = 0; i < n; i++) {
                arr[i] = Integer.parseInt(st.nextToken());
            }
        }
        
        int k = Integer.parseInt(br.readLine().trim());
        
        // Count frequency of each element
        Map<Integer, Integer> freq = new HashMap<>();
        for (int num : arr) {
            freq.put(num, freq.getOrDefault(num, 0) + 1);
        }
        
        // Collect unique elements
        List<Integer> unique = new ArrayList<>();
        for (Map.Entry<Integer, Integer> entry : freq.entrySet()) {
            if (entry.getValue() == 1) {
                unique.add(entry.getKey());
            }
        }
        
        // Sort unique elements
        Collections.sort(unique);
        
        // Return kth smallest or -1
        if (k <= 0 || k > unique.size()) {
            System.out.println(-1);
        } else {
            System.out.println(unique.get(k - 1));
        }
    }
}
