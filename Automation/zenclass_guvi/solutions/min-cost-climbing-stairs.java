import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        if (n == 0) {
            System.out.println(0);
            return;
        }
        
        String[] tokens = br.readLine().trim().split("\\s+");
        int[] cost = new int[n];
        for (int i = 0; i < n; i++) {
            cost[i] = Integer.parseInt(tokens[i]);
        }
        
        if (n == 1) {
            System.out.println(Math.min(cost[0], cost[0]));
            return;
        }
        
        if (n == 2) {
            System.out.println(Math.min(cost[0], cost[1]));
            return;
        }
        
        int prev2 = cost[0];
        int prev1 = cost[1];
        
        for (int i = 2; i < n; i++) {
            int current = cost[i] + Math.min(prev1, prev2);
            prev2 = prev1;
            prev1 = current;
        }
        
        System.out.println(Math.min(prev1, prev2));
    }
}
