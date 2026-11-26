import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        
        if (line == null || line.trim().isEmpty()) {
            System.out.println(-1);
            return;
        }
        
        StringTokenizer st = new StringTokenizer(line);
        int n = st.countTokens();
        
        if (n == 0) {
            System.out.println(-1);
            return;
        }
        
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }
        
        int rotations = findRotationCount(arr);
        System.out.println(rotations);
    }
    
    private static int findRotationCount(int[] arr) {
        int low = 0;
        int high = arr.length - 1;
        
        // If the array is not rotated (or has one element)
        if (arr.length <= 1 || arr[low] <= arr[high]) {
            return 0;
        }
        
        while (low <= high) {
            int mid = low + (high - low) / 2;
            int next = (mid + 1) % arr.length;
            int prev = (mid - 1 + arr.length) % arr.length;
            
            // Check if mid is the minimum element
            if (arr[mid] <= arr[next] && arr[mid] <= arr[prev]) {
                return mid;
            }
            
            // Decide which side to go to
            if (arr[mid] <= arr[high]) {
                // Right half is sorted, minimum is in left half
                high = mid - 1;
            } else {
                // Left half is sorted, minimum is in right half
                low = mid + 1;
            }
        }
        
        return 0;  // Should not reach here for valid inputs
    }
}
