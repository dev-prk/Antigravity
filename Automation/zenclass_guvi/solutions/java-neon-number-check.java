import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextLong()) {
            System.out.println("Not a Neon Number");
            return;
        }
        
        long n = sc.nextLong();
        
        if (n < 0) {
            System.out.println("Not a Neon Number");
            return;
        }
        
        long square = n * n;
        long sum = 0;
        
        while (square > 0) {
            sum += square % 10;
            square /= 10;
        }
        
        if (sum == n) {
            System.out.println("Neon Number");
        } else {
            System.out.println("Not a Neon Number");
        }
    }
}
