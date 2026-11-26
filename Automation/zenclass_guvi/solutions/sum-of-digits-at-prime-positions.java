import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            System.out.println(0);
            return;
        }
        line = line.trim();
        if (line.isEmpty()) {
            System.out.println(0);
            return;
        }
        int len = line.length();
        if (len == 0) {
            System.out.println(0);
            return;
        }
        boolean[] isPrime = new boolean[len + 1];
        if (len >= 2) {
            Arrays.fill(isPrime, true);
            isPrime[0] = false;
            isPrime[1] = false;
            for (int i = 2; i * i <= len; i++) {
                if (isPrime[i]) {
                    for (int j = i * i; j <= len; j += i) {
                        isPrime[j] = false;
                    }
                }
            }
        }
        int sum = 0;
        for (int i = 1; i <= len; i++) {
            if (isPrime[i]) {
                sum += line.charAt(i - 1) - '0';
            }
        }
        System.out.println(sum);
    }
}
