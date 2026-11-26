import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class Main {
    private static Map<Integer, Long> memo = new HashMap<>();
    
    public static long fibonacci(int n) {
        if (n <= 2) {
            return 1;
        }
        
        if (memo.containsKey(n)) {
            return memo.get(n);
        }
        
        long result = fibonacci(n - 1) + fibonacci(n - 2);
        memo.put(n, result);
        return result;
    }
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        while (scanner.hasNextInt()) {
            int n = scanner.nextInt();
            System.out.println(fibonacci(n));
        }
        
        scanner.close();
    }
}
