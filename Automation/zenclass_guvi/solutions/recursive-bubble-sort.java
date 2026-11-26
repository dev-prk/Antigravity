import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }
        recursiveBubbleSort(arr, n);
        for (int i = 0; i < n; i++) {
            System.out.print(arr[i]);
            if (i < n - 1) {
                System.out.print(" ");
            }
        }
        System.out.println();
    }
    
    public static void recursiveBubbleSort(int[] arr, int n) {
        if (n <= 1) {
            return;
        }
        recursiveBubbleSort(arr, n - 1);
        if (arr[n - 2] > arr[n - 1]) {
            int temp = arr[n - 2];
            arr[n - 2] = arr[n - 1];
            arr[n - 1] = temp;
        }
        recursiveBubbleSort(arr, n - 1);
    }
}
