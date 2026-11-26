import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        int a = scanner.nextInt();
        int b = scanner.nextInt();
        int c = scanner.nextInt();
        
        // Apply transformations based on conditions
        if (a % 2 == 0) {
            a = a + b;
        }
        
        if (b % 2 != 0) {
            c = c * 2;
        }
        
        if (c % 3 == 0) {
            c = c + a;
        }
        
        // Check if sum is greater than 100
        if (a + b + c > 100) {
            a = a - 100;
            b = b - 100;
            c = c - 100;
        }
        
        System.out.println("a: " + a + ", b: " + b + ", c: " + c);
        
        scanner.close();
    }
}
