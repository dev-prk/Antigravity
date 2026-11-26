import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        int n = Integer.parseInt(br.readLine().trim());
        
        int[] arr1 = new int[n];
        int[] arr2 = new int[n];
        
        StringTokenizer st1 = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr1[i] = Integer.parseInt(st1.nextToken());
        }
        
        StringTokenizer st2 = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr2[i] = Integer.parseInt(st2.nextToken());
        }
        
        boolean isMirror = true;
        for (int i = 0; i < n; i++) {
            if (arr1[i] != arr2[n - 1 - i]) {
                isMirror = false;
                break;
            }
        }
        
        System.out.println(isMirror ? "yes" : "no");
    }
}
