import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        // Read the input number
        long n = scanner.nextLong();
        
        // Handle negative numbers by taking absolute value
        n = Math.abs(n);
        
        // Calculate sum of digits
        int sum = 0;
        while (n > 0) {
            sum += n % 10;
            n /= 10;
        }
        
        // Print the result
        System.out.println(sum);
        
        scanner.close();
    }
}
