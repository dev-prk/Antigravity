import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            System.out.println("false");
            return;
        }
        int n = Integer.parseInt(line.trim());
        System.out.println(isArmstrong(n));
    }

    private static boolean isArmstrong(int n) {
        if (n < 0) return false;
        int original = n;
        int digits = 0;
        int temp = n;
        if (temp == 0) {
            digits = 1;
        } else {
            while (temp > 0) {
                digits++;
                temp /= 10;
            }
        }
        long sum = 0;
        temp = n;
        while (temp > 0) {
            int digit = temp % 10;
            sum += pow(digit, digits);
            temp /= 10;
        }
        return sum == original;
    }

    private static long pow(int base, int exp) {
        long result = 1;
        long b = base;
        while (exp > 0) {
            if ((exp & 1) == 1) {
                result *= b;
            }
            b *= b;
            exp >>= 1;
        }
        return result;
    }
}
