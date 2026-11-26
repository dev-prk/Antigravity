import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(parts[0]);
        int s = Integer.parseInt(parts[1]);
        
        if (n == 0) {
            System.out.println(s == 0 ? "Yes" : "No");
            return;
        }
        
        int[] arr = new int[n];
        String[] nums = br.readLine().trim().split("\\s+");
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(nums[i]);
        }
        
        // Handle negative target sum
        int target = Math.abs(s);
        
        // Find max positive and min negative values to determine offset
        int offset = 0;
        for (int x : arr) {
            if (x < 0) {
                offset += x;
            }
        }
        
        // If target sum is 0, always possible (empty subset)
        if (s == 0) {
            System.out.println("Yes");
            return;
        }
        
        // For simplicity, use subset sum approach that handles both positive and negative
        // We'll use a different approach: track all possible sums
        Set<Integer> sums = new HashSet<>();
        sums.add(0);
        
        for (int x : arr) {
            Set<Integer> newSums = new HashSet<>(sums);
            for (int sum : sums) {
                newSums.add(sum + x);
            }
            sums = newSums;
        }
        
        System.out.println(sums.contains(s) ? "Yes" : "No");
    }
}
