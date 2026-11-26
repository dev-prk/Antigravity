import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        String[] arrStr = sc.nextLine().trim().split("\\s+");
        int[] arr = new int[arrStr.length];
        for (int i = 0; i < arrStr.length; i++) {
            arr[i] = Integer.parseInt(arrStr[i]);
        }
        int target = sc.nextInt();
        
        int first = -1;
        int last = -1;
        
        // Find first occurrence
        int left = 0;
        int right = arr.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                first = mid;
                right = mid - 1;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        // Find last occurrence
        left = 0;
        right = arr.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                last = mid;
                left = mid + 1;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        System.out.println(first + " " + last);
    }
}
