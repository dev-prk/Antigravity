import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(parts[0]);
        int w = Integer.parseInt(parts[1]);
        
        int[] values = new int[n];
        int[] weights = new int[n];
        
        if (n > 0) {
            parts = br.readLine().trim().split("\\s+");
            for (int i = 0; i < n; i++) {
                values[i] = Integer.parseInt(parts[i]);
            }
            
            parts = br.readLine().trim().split("\\s+");
            for (int i = 0; i < n; i++) {
                weights[i] = Integer.parseInt(parts[i]);
            }
        }
        
        int[] dp = new int[w + 1];
        
        for (int i = 0; i < n; i++) {
            for (int j = w; j >= weights[i]; j--) {
                dp[j] = Math.max(dp[j], dp[j - weights[i]] + values[i]);
            }
        }
        
        System.out.println(dp[w]);
    }
}
