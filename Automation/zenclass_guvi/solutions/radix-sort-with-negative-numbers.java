import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        String[] tokens = br.readLine().trim().split("\\s+");
        
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(tokens[i]);
        }
        
        radixSort(arr);
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(arr[i]);
        }
        System.out.println(sb.toString());
    }
    
    static void radixSort(int[] arr) {
        int n = arr.length;
        if (n == 0) return;
        
        // Separate negatives and non-negatives
        int[] negatives = new int[n];
        int[] nonNegatives = new int[n];
        int negCount = 0, nonNegCount = 0;
        
        for (int num : arr) {
            if (num < 0) {
                negatives[negCount++] = -num; // store absolute value
            } else {
                nonNegatives[nonNegCount++] = num;
            }
        }
        
        // Sort negatives (in reverse order after sorting absolute values)
        if (negCount > 0) {
            radixSortInPlace(negatives, negCount);
            // Reverse to get ascending order for negative numbers
            for (int i = 0; i < negCount / 2; i++) {
                int temp = negatives[i];
                negatives[i] = negatives[negCount - 1 - i];
                negatives[negCount - 1 - i] = temp;
            }
            // Apply negative sign
            for (int i = 0; i < negCount; i++) {
                negatives[i] = -negatives[i];
            }
        }
        
        // Sort non-negatives
        if (nonNegCount > 0) {
            radixSortInPlace(nonNegatives, nonNegCount);
        }
        
        // Merge the two sorted arrays
        int idx = 0;
        for (int i = 0; i < negCount; i++) {
            arr[idx++] = negatives[i];
        }
        for (int i = 0; i < nonNegCount; i++) {
            arr[idx++] = nonNegatives[i];
        }
    }
    
    static void radixSortInPlace(int[] arr, int n) {
        if (n == 0) return;
        
        // Find maximum number to know number of digits
        int max = arr[0];
        for (int i = 1; i < n; i++) {
            if (arr[i] > max) max = arr[i];
        }
        
        // Do counting sort for every digit
        for (int exp = 1; max / exp > 0; exp *= 10) {
            countingSortByDigit(arr, n, exp);
        }
    }
    
    static void countingSortByDigit(int[] arr, int n, int exp) {
        int[] output = new int[n];
        int[] count = new int[10];
        
        // Store count of occurrences in count[]
        for (int i = 0; i < n; i++) {
            count[(arr[i] / exp) % 10]++;
        }
        
        // Change count[i] so that count[i] contains actual
        // position of this digit in output[]
        for (int i = 1; i < 10; i++) {
            count[i] += count[i - 1];
        }
        
        // Build output array
        for (int i = n - 1; i >= 0; i--) {
            output[count[(arr[i] / exp) % 10] - 1] = arr[i];
            count[(arr[i] / exp) % 10]--;
        }
        
        // Copy output array to arr[]
        for (int i = 0; i < n; i++) {
            arr[i] = output[i];
        }
    }
}
