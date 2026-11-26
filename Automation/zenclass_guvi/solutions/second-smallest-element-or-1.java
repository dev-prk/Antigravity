import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        if (n <= 1) {
            System.out.println(-1);
            return;
        }
        
        String[] tokens = br.readLine().trim().split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(tokens[i]);
        }
        
        int min = arr[0];
        int secondMin = Integer.MAX_VALUE;
        
        for (int i = 1; i < n; i++) {
            if (arr[i] < min) {
                secondMin = min;
                min = arr[i];
            } else if (arr[i] > min && arr[i] < secondMin) {
                secondMin = arr[i];
            }
        }
        
        if (secondMin == Integer.MAX_VALUE) {
            System.out.println(-1);
        } else {
            System.out.println(secondMin);
        }
    }
}
