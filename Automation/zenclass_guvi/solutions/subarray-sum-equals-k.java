import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] nk = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(nk[0]);
        int k = Integer.parseInt(nk[1]);
        
        String[] tokens = br.readLine().trim().split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(tokens[i]);
        }
        
        Map<Integer, Integer> prefixSumCount = new HashMap<>();
        prefixSumCount.put(0, 1);
        
        int sum = 0;
        int count = 0;
        
        for (int i = 0; i < n; i++) {
            sum += arr[i];
            
            if (prefixSumCount.containsKey(sum - k)) {
                count += prefixSumCount.get(sum - k);
            }
            
            prefixSumCount.put(sum, prefixSumCount.getOrDefault(sum, 0) + 1);
        }
        
        System.out.println(count);
    }
}
