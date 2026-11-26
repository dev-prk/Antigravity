import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] line1 = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(line1[0]);
        int amount = Integer.parseInt(line1[1]);
        
        if (amount == 0) {
            System.out.println(0);
            return;
        }
        
        int[] coins = new int[n];
        String[] line2 = br.readLine().trim().split("\\s+");
        for (int i = 0; i < n; i++) {
            coins[i] = Integer.parseInt(line2[i]);
        }
        
        Arrays.sort(coins);
        int count = 0;
        int remaining = amount;
        
        for (int i = n - 1; i >= 0; i--) {
            if (coins[i] <= remaining) {
                count += remaining / coins[i];
                remaining %= coins[i];
            }
            if (remaining == 0) break;
        }
        
        if (remaining == 0) {
            System.out.println(count);
        } else {
            System.out.println(-1);
        }
    }
}
