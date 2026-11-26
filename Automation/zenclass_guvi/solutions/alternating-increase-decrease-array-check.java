import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nStr = br.readLine();
        if (nStr == null || nStr.isEmpty()) {
            System.out.println("yes");
            return;
        }
        int n = Integer.parseInt(nStr.trim());
        if (n <= 1) {
            System.out.println("yes");
            return;
        }
        
        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            if (st.hasMoreTokens()) {
                arr[i] = Integer.parseInt(st.nextToken());
            }
        }
        
        boolean valid = true;
        for (int i = 0; i < n - 1; i++) {
            if (i % 2 == 0) {
                // position i should be less than position i+1 (increase)
                if (arr[i] >= arr[i + 1]) {
                    valid = false;
                    break;
                }
            } else {
                // position i should be greater than position i+1 (decrease)
                if (arr[i] <= arr[i + 1]) {
                    valid = false;
                    break;
                }
            }
        }
        
        System.out.println(valid ? "yes" : "no");
    }
}
