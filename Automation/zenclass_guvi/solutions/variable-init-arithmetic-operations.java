import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) {
            return;
        }
        int a = sc.nextInt();
        int b = sc.hasNextInt() ? sc.nextInt() : 0;
        int c = sc.hasNextInt() ? sc.nextInt() : 0;
        int d = sc.hasNextInt() ? sc.nextInt() : 0;

        int op1 = (a + b) * c;
        int op2 = a != 0 ? (b - d) / a : 0;
        int op3 = a * d + c;
        int op4 = (a + b + c + d) / 2;

        System.out.println("Result of operation 1: " + op1);
        System.out.println("Result of operation 2: " + op2);
        System.out.println("Result of operation 3: " + op3);
        System.out.println("Result of operation 4: " + op4);
    }
}
