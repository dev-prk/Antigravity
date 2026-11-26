import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String line = sc.nextLine().trim();
        sc.close();

        if (line.isEmpty()) {
            System.out.println("Not a Disarium Number");
            return;
        }

        try {
            int n = Integer.parseInt(line);

            if (n <= 0) {
                System.out.println("Not a Disarium Number");
                return;
            }

            int temp = n;
            int digits = 0;
            while (temp > 0) {
                digits++;
                temp /= 10;
            }

            temp = n;
            long sum = 0;
            int pos = digits;

            while (temp > 0) {
                int d = temp % 10;
                int p = 1;
                for (int i = 0; i < pos; i++) {
                    p *= d;
                }
                sum += p;
                temp /= 10;
                pos--;
            }

            if (sum == n) {
                System.out.println("Disarium Number");
            } else {
                System.out.println("Not a Disarium Number");
            }
        } catch (NumberFormatException e) {
            System.out.println("Not a Disarium Number");
        }
    }
}
