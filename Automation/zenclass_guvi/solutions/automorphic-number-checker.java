import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int square = n * n;
        int temp = n;
        int digits = 0;
        while (temp > 0) {
            digits++;
            temp /= 10;
        }
        int divisor = 1;
        for (int i = 0; i < digits; i++) {
            divisor *= 10;
        }
        int lastDigits = square % divisor;
        if (lastDigits == n) {
            System.out.println("Automorphic Number");
        } else {
            System.out.println("Not an Automorphic Number");
        }
        sc.close();
    }
}
