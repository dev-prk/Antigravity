import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] nk = br.readLine().trim().split("\\s+");
        int N = Integer.parseInt(nk[0]);
        int K = Integer.parseInt(nk[1]);
        
        int[] arr = new int[N];
        if (N > 0) {
            String[] parts = br.readLine().trim().split("\\s+");
            for (int i = 0; i < N; i++) {
                arr[i] = Integer.parseInt(parts[i]);
            }
        }
        
        // Prefix sums: ps[i] = sum of arr[0..i-1]
        long[] ps = new long[N + 1];
        for (int i = 1; i <= N; i++) {
            ps[i] = ps[i - 1] + arr[i - 1];
        }
        
        // dp[i][j] = min cost to partition arr[0..i-1] into j segments
        long[][] dp = new long[N + 1][K + 1];
        final long INF = Long.MAX_VALUE / 4;
        
        // Base case: 0 elements, 0 segments
        dp[0][0] = 0;
        
        // For 1 segment, dp[i][1] = cost of segment [0..i-1]
        for (int i = 1; i <= N; i++) {
            dp[i][1] = (ps[i] - ps[0]) * i; // sum * length
        }
        
        // Fill dp for j = 2 to K
        for (int j = 2; j <= K; j++) {
            for (int i = j; i <= N; i++) { // need at least j elements for j segments
                dp[i][j] = INF;
                for (int k = j - 1; k < i; k++) { // partition at k: [0..k-1] and [k..i-1]
                    long cost = dp[k][j - 1] + (ps[i] - ps[k]) * (i - k);
                    if (cost < dp[i][j]) {
                        dp[i][j] = cost;
                    }
                }
            }
        }
        
        System.out.println(dp[N][K]);
    }
}
