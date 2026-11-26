import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long L = sc.nextLong();
        long R = sc.nextLong();
        sc.close();
        
        long firstOdd = (L % 2 == 1) ? L : L + 1;
        long lastOdd = (R % 2 == 1) ? R : R - 1;
        
        if (firstOdd > lastOdd) {
            System.out.println(0);
        } else {
            long n = ((lastOdd - firstOdd) / 2) + 1;
            long sum = (n * (firstOdd + lastOdd)) / 2;
            System.out.println(sum);
        }
    }
}
