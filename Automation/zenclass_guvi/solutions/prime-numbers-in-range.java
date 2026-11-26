import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int start = Integer.parseInt(parts[0]);
        int end = Integer.parseInt(parts[1]);
        
        List<Integer> primes = new ArrayList<>();
        for (int i = start; i <= end; i++) {
            if (isPrime(i)) {
                primes.add(i);
            }
        }
        
        for (int i = 0; i < primes.size(); i++) {
            if (i > 0) System.out.println();
            System.out.print(primes.get(i));
        }
        if (!primes.isEmpty()) System.out.println();
    }
    
    static boolean isPrime(int n) {
        if (n < 2) return false;
        if (n == 2) return true;
        if (n % 2 == 0) return false;
        for (int i = 3; i * i <= n; i += 2) {
            if (n % i == 0) return false;
        }
        return true;
    }
}
