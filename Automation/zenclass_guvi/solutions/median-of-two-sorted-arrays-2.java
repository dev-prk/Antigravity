import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        int n1 = Integer.parseInt(br.readLine().trim());
        int[] nums1 = new int[n1];
        if (n1 > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int i = 0; i < n1; i++) {
                nums1[i] = Integer.parseInt(st.nextToken());
            }
        }
        
        int n2 = Integer.parseInt(br.readLine().trim());
        int[] nums2 = new int[n2];
        if (n2 > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int i = 0; i < n2; i++) {
                nums2[i] = Integer.parseInt(st.nextToken());
            }
        }
        
        double median = findMedian(nums1, nums2);
        System.out.println(median);
    }
    
    private static double findMedian(int[] nums1, int[] nums2) {
        int m = nums1.length;
        int n = nums2.length;
        
        // Ensure nums1 is the smaller array
        if (m > n) {
            return findMedian(nums2, nums1);
        }
        
        int total = m + n;
        int half = (total + 1) / 2;
        
        int low = 0, high = m;
        
        while (low <= high) {
            int partition1 = (low + high) / 2;
            int partition2 = half - partition1;
            
            // Handle edge cases with Integer.MIN_VALUE and Integer.MAX_VALUE
            int maxLeft1 = (partition1 == 0) ? Integer.MIN_VALUE : nums1[partition1 - 1];
            int minRight1 = (partition1 == m) ? Integer.MAX_VALUE : nums1[partition1];
            
            int maxLeft2 = (partition2 == 0) ? Integer.MIN_VALUE : nums2[partition2 - 1];
            int minRight2 = (partition2 == n) ? Integer.MAX_VALUE : nums2[partition2];
            
            if (maxLeft1 <= minRight2 && maxLeft2 <= minRight1) {
                // Found correct partition
                if (total % 2 == 1) {
                    return Math.max(maxLeft1, maxLeft2);
                } else {
                    return (Math.max(maxLeft1, maxLeft2) + Math.min(minRight1, minRight2)) / 2.0;
                }
            } else if (maxLeft1 > minRight2) {
                // Need to move partition1 to the left
                high = partition1 - 1;
            } else {
                // Need to move partition1 to the right
                low = partition1 + 1;
            }
        }
        
        return 0.0; // Should never reach here
    }
}
