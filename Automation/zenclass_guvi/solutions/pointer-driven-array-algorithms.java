import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        int x = sc.nextInt();
        
        Arrays.sort(arr);
        
        System.out.print("Sorted array: ");
        for (int i = 0; i < n; i++) {
            if (i > 0) System.out.print(" ");
            System.out.print(arr[i]);
        }
        System.out.println(" ");
        
        double median;
        if (n % 2 == 1) {
            median = arr[n / 2];
        } else {
            median = (arr[n / 2 - 1] + arr[n / 2]) / 2.0;
        }
        System.out.printf("Median: %.2f%n", median);
        
        int result = binarySearch(arr, x);
        System.out.println("Binary Search Result: " + result);
    }
    
    static int binarySearch(int[] arr, int x) {
        int left = 0;
        int right = arr.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == x) {
                return mid;
            } else if (arr[mid] < x) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }
}
