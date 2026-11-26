import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int m = scanner.nextInt();
        int n = scanner.nextInt();
        
        int total = m + n - 2;
        int k = Math.min(m - 1, n - 1);
        
        long result = 1;
        for (int i = 1; i <= k; i++) {
            result = result * (total - i + 1) / i;
        }
        
        System.out.println(result);
    }
}
