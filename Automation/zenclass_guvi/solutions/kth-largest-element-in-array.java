import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] nk = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(nk[0]);
        int k = Integer.parseInt(nk[1]);
        
        String[] nums = br.readLine().trim().split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(nums[i]);
        }
        
        Arrays.sort(arr);
        System.out.println(arr[n - k]);
    }
}
