import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
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
        
        int[][] cost = new int[n][n];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                cost[i][j] = Integer.parseInt(st.nextToken());
            }
        }
        
        int total_masks = 1 << n;
        long[] dp = new long[total_masks];
        Arrays.fill(dp, Long.MAX_VALUE);
        dp[0] = 0;
        
        for (int mask = 0; mask < total_masks; mask++) {
            int task = Integer.bitCount(mask);
            if (task >= n) continue;
            for (int person = 0; person < n; person++) {
                if ((mask & (1 << person)) == 0) {
                    int new_mask = mask | (1 << person);
                    if (dp[mask] != Long.MAX_VALUE) {
                        dp[new_mask] = Math.min(dp[new_mask], dp[mask] + cost[task][person]);
                    }
                }
            }
        }
        
        System.out.println(dp[total_masks - 1]);
    }
}
