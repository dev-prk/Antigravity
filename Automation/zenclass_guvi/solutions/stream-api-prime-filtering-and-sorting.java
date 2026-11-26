import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        List<Integer> list = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            list.add(sc.nextInt());
        }
        //..... YOUR CODE STARTS HERE .....
        
        List<Integer> primes = list.stream()
            .filter(Main::isPrime)
            .sorted(Collections.reverseOrder())
            .collect(Collectors.toList());
        
        for (int prime : primes) {
            System.out.println(prime);
        }
        
        //..... YOUR CODE ENDS HERE .....
    }

    public static boolean isPrime(int num) {
        //..... YOUR CODE STARTS HERE .....
        if (num <= 1) {
            return false;
        }
        if (num <= 3) {
            return true;
        }
        if (num % 2 == 0 || num % 3 == 0) {
            return false;
        }
        for (int i = 5; i * i <= num; i += 6) {
            if (num % i == 0 || num % (i + 2) == 0) {
                return false;
            }
        }
        return true;
        //..... YOUR CODE ENDS HERE .....
    }
}
