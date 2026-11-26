import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();
        sc.close();
        
        long sum = 0;
        n = Math.abs(n);
        
        while (n > 0) {
            sum += n % 10;
            n /= 10;
        }
        
        System.out.println(sum);
    }
}
