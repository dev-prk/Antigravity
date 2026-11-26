import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        // Read three boolean values (as strings)
        boolean[] flags = new boolean[3];
        int count = 0;
        for (int i = 0; i < 3; i++) {
            if (scanner.hasNext()) {
                String token = scanner.next();
                flags[i] = Boolean.parseBoolean(token);
                if (flags[i]) count++;
            }
        }
        // Qualify if at least two are true
        System.out.println(count >= 2);
        scanner.close();
    }
}
