import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextInt()) {
            System.out.println(-1);
            return;
        }
        
        int n = sc.nextInt();
        int[] arr = new int[n];
        
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        
        Map<Integer, Integer> freq = new HashMap<>();
        for (int num : arr) {
            freq.put(num, freq.getOrDefault(num, 0) + 1);
        }
        
        List<Integer> keys = new ArrayList<>(freq.keySet());
        Collections.sort(keys);
        
        for (int key : keys) {
            System.out.println(key + ": " + freq.get(key));
        }
    }
}
