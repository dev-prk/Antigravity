import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nStr = br.readLine();
        if (nStr == null || nStr.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(nStr.trim());
        if (n <= 0) {
            System.out.println(0);
            return;
        }
        
        String[] tokens = br.readLine().trim().split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(tokens[i]);
        }
        
        System.out.println(minSwaps(arr));
    }
    
    static int minSwaps(int[] arr) {
        int n = arr.length;
        int[] sorted = arr.clone();
        Arrays.sort(sorted);
        
        // Create a map from value to its sorted index
        int[] indexMap = new int[sorted[n - 1] + 1];
        for (int i = 0; i < n; i++) {
            indexMap[sorted[i]] = i;
        }
        
        boolean[] visited = new boolean[n];
        int swaps = 0;
        
        for (int i = 0; i < n; i++) {
            // If element is already in correct position or already visited
            if (visited[i] || indexMap[arr[i]] == i) {
                visited[i] = true;
                continue;
            }
            
            // Count nodes in the cycle
            int cycleSize = 0;
            int j = i;
            while (!visited[j]) {
                visited[j] = true;
                j = indexMap[arr[j]];
                cycleSize++;
            }
            
            // Add to swaps
            if (cycleSize > 0) {
                swaps += (cycleSize - 1);
            }
        }
        
        return swaps;
    }
}
