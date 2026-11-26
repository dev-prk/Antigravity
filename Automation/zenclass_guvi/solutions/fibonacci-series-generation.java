import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        if (!scanner.hasNextInt()) {
            scanner.close();
            return;
        }
        
        int n = scanner.nextInt();
        scanner.close();
        
        if (n <= 0) {
            return;
        }
        
        int a = 0, b = 1;
        
        for (int i = 0; i < n; i++) {
            System.out.print(a);
            if (i < n - 1) {
                System.out.print(" ");
            }
            int next = a + b;
            a = b;
            b = next;
        }
        
        System.out.println();
    }
}
