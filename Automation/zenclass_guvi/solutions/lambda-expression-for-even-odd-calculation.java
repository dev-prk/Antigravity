import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        
        // Lambda for even numbers: sum them
        java.util.function.IntPredicate isEven = x -> x % 2 == 0;
        // Lambda for odd numbers
        java.util.function.IntPredicate isOdd = x -> x % 2 != 0;
        
        // Sum of even numbers
        int sumEven = Arrays.stream(arr)
                .filter(isEven)
                .sum();
        
        // Product of odd numbers
        int productOdd = Arrays.stream(arr)
                .filter(isOdd)
                .reduce(1, (a, b) -> a * b);
        
        // Difference: sum of even - product of odd
        int result = sumEven - productOdd;
        
        System.out.println(result);
    }
}
