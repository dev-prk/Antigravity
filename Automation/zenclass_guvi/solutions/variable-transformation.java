import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        int a = scanner.nextInt();
        int b = scanner.nextInt();
        int c = scanner.nextInt();
        
        // If a is even, add b to a
        if (a % 2 == 0) {
            a = a + b;
        }
        
        // If b is odd, multiply c by 2
        if (b % 2 != 0) {
            c = c * 2;
        }
        
        // If c is a multiple of 3, add a to c
        if (c % 3 == 0) {
            c = c + a;
        }
        
        // If the sum of a, b, and c is greater than 100, subtract 100 from each
        if (a + b + c > 100) {
            a = a - 100;
            b = b - 100;
            c = c - 100;
        }
        
        System.out.println("a: " + a + ", b: " + b + ", c: " + c);
    }
}
