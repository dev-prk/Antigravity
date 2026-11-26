import java.util.*;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextLong()) {
            sc.close();
            return;
        }
        long N = sc.nextLong();
        sc.close();
        if (N < 2) {
            System.out.println(0);
            return;
        }
        long K = N / 2;
        long sum = K * (K + 1);
        System.out.println(sum);
    }
}
