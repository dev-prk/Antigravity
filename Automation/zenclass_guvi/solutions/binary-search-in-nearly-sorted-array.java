public class Main {
    public static void main(String[] args) {
        java.util.Scanner sc = new java.util.Scanner(System.in);
        
        if (!sc.hasNextLine()) {
            System.out.println(-1);
            return;
        }
        
        String line1 = sc.nextLine().trim();
        if (line1.isEmpty()) {
            System.out.println(-1);
            return;
        }
        
        String[] parts = line1.split("\\s+");
        int[] arr = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            arr[i] = Integer.parseInt(parts[i]);
        }
        
        if (!sc.hasNextLine()) {
            System.out.println(-1);
            return;
        }
        
        String line2 = sc.nextLine().trim();
        if (line2.isEmpty()) {
            System.out.println(-1);
            return;
        }
        
        int target = Integer.parseInt(line2);
        
        System.out.println(searchNearlySorted(arr, target));
        sc.close();
    }
    
    public static int searchNearlySorted(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (arr[mid] == target) {
                return mid;
            }
            
            // Check if mid-1 has the target (only if arr is nearly sorted)
            if (mid - 1 >= left && arr[mid - 1] == target) {
                return mid - 1;
            }
            
            // Check if mid+1 has the target
            if (mid + 1 <= right && arr[mid + 1] == target) {
                return mid + 1;
            }
            
            // Determine which half to search
            if (target < arr[mid]) {
                // Target could be in left half or at mid-1
                // But we already checked mid-1, so search left excluding mid-1
                right = mid - 2;
            } else {
                // Target could be in right half or at mid+1
                // But we already checked mid+1, so search right excluding mid+1
                left = mid + 2;
            }
        }
        
        return -1;
    }
}
