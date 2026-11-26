import java.util.*;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();
        sc.close();
        if (n < 1) {
            System.out.println(0);
            return;
        }
        long k = (n + 1) / 2;
        System.out.println(k * k);
    }
}
