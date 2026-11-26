import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] nk = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(nk[0]);
        int k = Integer.parseInt(nk[1]);
        
        String[] tokens = br.readLine().trim().split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(tokens[i]);
        }
        
        int[] count = new int[k + 1];
        for (int num : arr) {
            count[num]++;
        }
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i <= k; i++) {
            for (int j = 0; j < count[i]; j++) {
                sb.append(i).append(" ");
            }
        }
        
        System.out.println(sb.toString().trim());
    }
}
