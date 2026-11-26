import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int N = sc.nextInt();
        
        if (N <= 0) {
            sc.close();
            return;
        }
        
        Integer[] arr = new Integer[N];
        for (int i = 0; i < N; i++) {
            arr[i] = sc.nextInt();
        }
        
        int min = arr[0];
        int max = arr[0];
        
        for (int i = 1; i < N; i++) {
            if (arr[i] < min) {
                min = arr[i];
            }
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        
        System.out.println("Min: " + min);
        System.out.println("Max: " + max);
        
        for (int val : arr) {
            String sign;
            if (val < 0) {
                sign = "Negative";
            } else if (val > 0) {
                sign = "Positive";
            } else {
                sign = "Zero";
            }
            System.out.println(val + ": " + sign);
        }
        
        sc.close();
    }
}
