import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) {
        try (BufferedReader br = new BufferedReader(new InputStreamReader(System.in))) {
            String line = br.readLine();
            if (line == null) {
                System.out.println(0);
                return;
            }
            line = line.trim();
            if (line.isEmpty()) {
                System.out.println(0);
                return;
            }
            int len = line.length();
            int pairs = len / 2;
            int sum = 0;
            for (int i = 0; i < pairs; i++) {
                int d1 = line.charAt(i * 2) - '0';
                int d2 = line.charAt(i * 2 + 1) - '0';
                sum += Math.abs(d1 - d2);
            }
            System.out.println(sum);
        } catch (IOException e) {
            System.out.println(0);
        }
    }
}
