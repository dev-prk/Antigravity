import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextInt()) {
            sc.close();
            return;
        }
        
        int n = sc.nextInt();
        
        if (n <= 0) {
            sc.close();
            return;
        }
        
        int min = Integer.MAX_VALUE;
        int max = Integer.MIN_VALUE;
        
        for (int i = 0; i < n; i++) {
            if (sc.hasNextInt()) {
                int val = sc.nextInt();
                if (val < min) min = val;
                if (val > max) max = val;
            }
        }
        
        System.out.println(min + " " + max);
        sc.close();
    }
}
