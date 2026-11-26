import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        try {
            String line = br.readLine();
            if (line == null) return;
            line = line.trim();
            if (line.isEmpty()) return;
            long n = Long.parseLong(line);
            boolean neg = n < 0;
            long x = Math.abs(n);
            long rev = 0;
            while (x > 0) {
                rev = rev * 10 + (x % 10);
                x /= 10;
            }
            if (neg) rev = -rev;
            System.out.println(rev);
        } catch (Exception e) {
        }
    }
}
