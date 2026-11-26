import java.io.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null) {
            System.out.print(0);
            return;
        }
        line = line.trim();
        int evenSum = 0;
        int oddSum = 0;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c < '0' || c > '9') continue; // ignore non-digit characters if any
            int digit = c - '0';
            if ((i & 1) == 0) {
                evenSum += digit;
            } else {
                oddSum += digit;
            }
        }
        int diff = Math.abs(evenSum - oddSum);
        System.out.print(diff);
    }
}
