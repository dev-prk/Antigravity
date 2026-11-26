import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        int[][] dist = new int[n][n];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                dist[i][j] = Integer.parseInt(st.nextToken());
            }
        }
        
        // dp[mask][i] = minimum distance to reach city i having visited the cities in mask
        // mask is a bitmask where bit j is 1 if city j has been visited
        int[][] dp = new int[1 << n][n];
        
        // Initialize with a large value
        for (int[] row : dp) {
            Arrays.fill(row, Integer.MAX_VALUE);
        }
        
        // Start at city 0 with only city 0 visited
        dp[1][0] = 0;
        
        // Fill the DP table
        for (int mask = 0; mask < (1 << n); mask++) {
            for (int i = 0; i < n; i++) {
                if (dp[mask][i] == Integer.MAX_VALUE) continue;
                
                // Try to visit each unvisited city j from city i
                for (int j = 0; j < n; j++) {
                    if ((mask & (1 << j)) == 0) { // if city j is not visited
                        int newMask = mask | (1 << j);
                        dp[newMask][j] = Math.min(dp[newMask][j], dp[mask][i] + dist[i][j]);
                    }
                }
            }
        }
        
        // Find the minimum distance to return to city 0 after visiting all cities
        int allVisited = (1 << n) - 1;
        int ans = Integer.MAX_VALUE;
        
        for (int i = 0; i < n; i++) {
            if (dp[allVisited][i] != Integer.MAX_VALUE) {
                ans = Math.min(ans, dp[allVisited][i] + dist[i][0]);
            }
        }
        
        System.out.println(ans);
    }
}
