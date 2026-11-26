import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int r = sc.nextInt();
        int c = sc.nextInt();
        if (r <= 0 || c <= 0) {
            return;
        }
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                int val = sc.nextInt();
                if (j == 0) {
                    System.out.print(val);
                } else {
                    System.out.print(" " + val);
                }
            }
            System.out.println();
        }
    }
}
