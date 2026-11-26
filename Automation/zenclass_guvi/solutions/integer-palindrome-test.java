import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            System.out.println("NO");
            return;
        }
        int n = Integer.parseInt(line.trim());
        if (n < 0) {
            System.out.println("NO");
            return;
        }
        int original = n;
        int reversed = 0;
        while (n > 0) {
            reversed = reversed * 10 + n % 10;
            n /= 10;
        }
        if (original == reversed) {
            System.out.println("YES");
        } else {
            System.out.println("NO");
        }
    }
}
