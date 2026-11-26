import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String ns = br.readLine();
        if (ns == null || ns.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        int n = Integer.parseInt(ns.trim());
        if (n <= 0) {
            System.out.println(0);
            return;
        }
        String line = br.readLine();
        if (line == null || line.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        String[] parts = line.trim().split("\\s+");
        int[] arr = new int[n];
        for (int i = 0; i < n && i < parts.length; i++) {
            arr[i] = Integer.parseInt(parts[i]);
        }
        System.out.println(maxCircularSubarraySum(arr));
    }

    private static int maxCircularSubarraySum(int[] arr) {
        int n = arr.length;
        if (n == 0) return 0;
        if (n == 1) return arr[0];
        
        long total = 0;
        for (int v : arr) total += v;
        
        long maxNormal = kadaneMax(arr);
        long minSubarray = kadaneMin(arr);
        
        long circularSum = 0;
        if (total - minSubarray != 0) {
            circularSum = total - minSubarray;
        } else {
            circularSum = Long.MIN_VALUE;
        }
        
        long ans = Math.max(maxNormal, circularSum);
        return (int) ans;
    }
    
    private static long kadaneMax(int[] arr) {
        long max = arr[0];
        long cur = arr[0];
        for (int i = 1; i < arr.length; i++) {
            cur = Math.max(arr[i], cur + arr[i]);
            max = Math.max(max, cur);
        }
        return max;
    }
    
    private static long kadaneMin(int[] arr) {
        long min = arr[0];
        long cur = arr[0];
        for (int i = 1; i < arr.length; i++) {
            cur = Math.min(arr[i], cur + arr[i]);
            min = Math.min(min, cur);
        }
        return min;
    }
}
