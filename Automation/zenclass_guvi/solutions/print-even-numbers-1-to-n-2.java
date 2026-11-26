import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int n = sc.nextInt();
            for (int i = 2; i <= n; i += 2) {
                System.out.println(i);
            }
        }
        sc.close();
    }
}
