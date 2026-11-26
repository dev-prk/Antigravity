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
        
        int[] arr1 = arr.clone();
        int[] arr2 = arr.clone();
        
        // Bubble Sort
        long startTime1 = System.currentTimeMillis();
        bubbleSort(arr1);
        long endTime1 = System.currentTimeMillis();
        
        // Merge Sort
        long startTime2 = System.currentTimeMillis();
        mergeSort(arr2, 0, arr2.length - 1);
        long endTime2 = System.currentTimeMillis();
        
        // Output Bubble Sort result
        System.out.print("Bubble Sort: [");
        for (int i = 0; i < arr1.length; i++) {
            if (i > 0) System.out.print(", ");
            System.out.print(arr1[i]);
        }
        System.out.println("]");
        System.out.println("Time taken by Bubble Sort: " + (endTime1 - startTime1) + " ms");
        
        // Output Merge Sort result
        System.out.print("Merge Sort: [");
        for (int i = 0; i < arr2.length; i++) {
            if (i > 0) System.out.print(", ");
            System.out.print(arr2[i]);
        }
        System.out.println("]");
        System.out.println("Time taken by Merge Sort: " + (endTime2 - startTime2) + " ms");
        
        sc.close();
    }
    
    static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
    
    static void mergeSort(int[] arr, int left, int right) {
        if (left < right) {
            int mid = left + (right - left) / 2;
            mergeSort(arr, left, mid);
            mergeSort(arr, mid + 1, right);
            merge(arr, left, mid, right);
        }
    }
    
    static void merge(int[] arr, int left, int mid, int right) {
        int n1 = mid - left + 1;
        int n2 = right - mid;
        
        int[] L = new int[n1];
        int[] R = new int[n2];
        
        for (int i = 0; i < n1; i++) {
            L[i] = arr[left + i];
        }
        for (int j = 0; j < n2; j++) {
            R[j] = arr[mid + 1 + j];
        }
        
        int i = 0, j = 0, k = left;
        while (i < n1 && j < n2) {
            if (L[i] <= R[j]) {
                arr[k] = L[i];
                i++;
            } else {
                arr[k] = R[j];
                j++;
            }
            k++;
        }
        
        while (i < n1) {
            arr[k] = L[i];
            i++;
            k++;
        }
        
        while (j < n2) {
            arr[k] = R[j];
            j++;
            k++;
        }
    }
}
