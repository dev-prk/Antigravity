import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        if (n < 2) {
            System.out.println(-1);
            return;
        }
        
        String[] tokens = br.readLine().trim().split("\\s+");
        
        int max1 = Integer.MIN_VALUE;
        int max2 = Integer.MIN_VALUE;
        int min1 = Integer.MAX_VALUE;
        int min2 = Integer.MAX_VALUE;
        
        for (int i = 0; i < n && i < tokens.length; i++) {
            int x = Integer.parseInt(tokens[i]);
            
            if (x > max1) {
                max2 = max1;
                max1 = x;
            } else if (x > max2) {
                max2 = x;
            }
            
            if (x < min1) {
                min2 = min1;
                min1 = x;
            } else if (x < min2) {
                min2 = x;
            }
        }
        
        long product1 = (long) max1 * max2;
        long product2 = (long) min1 * min2;
        
        System.out.println(Math.max(product1, product2));
    }
}
