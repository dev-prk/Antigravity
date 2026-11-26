import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] nm = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(nm[0]);
        int m = Integer.parseInt(nm[1]);
        
        int[] arr1 = new int[n];
        int[] arr2 = new int[m];
        
        if (n > 0) {
            String[] s1 = br.readLine().trim().split("\\s+");
            for (int i = 0; i < n; i++) {
                arr1[i] = Integer.parseInt(s1[i]);
            }
        }
        
        if (m > 0) {
            String[] s2 = br.readLine().trim().split("\\s+");
            for (int i = 0; i < m; i++) {
                arr2[i] = Integer.parseInt(s2[i]);
            }
        }
        
        int[] result = new int[n + m];
        int i = 0, j = 0, k = 0;
        
        while (i < n && j < m) {
            if (arr1[i] <= arr2[j]) {
                result[k++] = arr1[i++];
            } else {
                result[k++] = arr2[j++];
            }
        }
        
        while (i < n) {
            result[k++] = arr1[i++];
        }
        
        while (j < m) {
            result[k++] = arr2[j++];
        }
        
        StringBuilder sb = new StringBuilder();
        for (int x : result) {
            sb.append(x).append(' ');
        }
        
        System.out.print(sb.toString().trim());
    }
}
