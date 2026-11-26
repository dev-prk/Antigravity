import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int[] arr = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            arr[i] = Integer.parseInt(parts[i]);
        }
        int target = Integer.parseInt(br.readLine().trim());
        
        int result = -1;
        int low = 0, high = 1;
        
        // Find the range where target might be
        while (high < arr.length && arr[high] < target) {
            low = high;
            high *= 2;
        }
        
        // Clamp high to array bounds
        if (high >= arr.length) {
            high = arr.length - 1;
        }
        
        // Binary search in the range [low, high]
        while (low <= high) {
            int mid = low + (high - low) / 2;
            if (arr[mid] == target) {
                result = mid;
                break;
            } else if (arr[mid] < target) {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        
        System.out.println(result);
    }
}
