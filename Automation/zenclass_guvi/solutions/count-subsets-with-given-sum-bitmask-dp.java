import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] nk = br.readLine().trim().split("\\s+");
        int N = Integer.parseInt(nk[0]);
        int K = Integer.parseInt(nk[1]);
        
        if (N == 0) {
            System.out.println(K == 0 ? 1 : 0);
            return;
        }
        
        String[] tokens = br.readLine().trim().split("\\s+");
        int[] arr = new int[N];
        for (int i = 0; i < N; i++) {
            arr[i] = Integer.parseInt(tokens[i]);
        }
        
        long[] dp = new long[K + 1];
        dp[0] = 1;
        
        for (int num : arr) {
            for (int s = K; s >= num; s--) {
                dp[s] += dp[s - num];
            }
        }
        
        System.out.println(dp[K]);
    }
}
