import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        int[] arr = new int[n];
        
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        
        Arrays.sort(arr);
        
        StringBuilder sb = new StringBuilder();
        for (int i = n - 1; i >= 0; i--) {
            sb.append(arr[i]);
            if (i > 0) {
                sb.append(" ");
            }
        }
        
        System.out.println(sb.toString());
        sc.close();
    }
}
