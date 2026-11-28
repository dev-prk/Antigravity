import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        int n = Integer.parseInt(br.readLine().trim());
        
        int[] arr = new int[n];
        if (n > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int i = 0; i < n; i++) {
                arr[i] = Integer.parseInt(st.nextToken());
            }
        }
        
        int m = Integer.parseInt(br.readLine().trim());
        
        for (int cmd = 0; cmd < m; cmd++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int start = Integer.parseInt(st.nextToken());
            int end = Integer.parseInt(st.nextToken());
            int k = Integer.parseInt(st.nextToken());
            
            // Calculate length of subarray
            int len = end - start + 1;
            if (len > 0) {
                // Normalize k to avoid unnecessary full rotations
                k = k % len;
                if (k < 0) {
                    k += len;
                }
                
                // Perform right rotation on subarray [start, end]
                if (k > 0) {
                    // Extract subarray
                    int[] temp = new int[len];
                    for (int i = 0; i < len; i++) {
                        temp[i] = arr[start + i];
                    }
                    
                    // Rotate right by k in temp array
                    int[] rotated = new int[len];
                    for (int i = 0; i < len; i++) {
                        rotated[(i + k) % len] = temp[i];
                    }
                    
                    // Copy back to original array
                    for (int i = 0; i < len; i++) {
                        arr[start + i] = rotated[i];
                    }
                }
            }
        }
        
        // Print result with trailing space
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(arr[i]);
            if (i < n - 1) {
                sb.append(" ");
            }
        }
        sb.append(" ");
        System.out.print(sb.toString());
    }
}
