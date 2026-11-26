import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        
        if (line == null || line.trim().isEmpty()) {
            System.out.println(-1);
            return;
        }
        
        String[] parts = line.trim().split("\\s+");
        int[] arr = new int[parts.length];
        
        for (int i = 0; i < parts.length; i++) {
            arr[i] = Integer.parseInt(parts[i]);
        }
        
        if (arr.length == 0) {
            System.out.println(-1);
            return;
        }
        
        if (arr.length == 1) {
            System.out.println(0);
            return;
        }
        
        int left = 0;
        int right = arr.length - 1;
        
        while (left < right) {
            int mid1 = left + (right - left) / 3;
            int mid2 = right - (right - left) / 3;
            
            if (arr[mid1] < arr[mid2]) {
                left = mid1 + 1;
            } else {
                right = mid2 - 1;
            }
        }
        
        System.out.println(left);
    }
}
