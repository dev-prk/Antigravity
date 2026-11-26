import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        while (sc.hasNextInt()) {
            int n = sc.nextInt();
            if (n == -1) break;
            
            List<Integer> scores = new ArrayList<>();
            for (int i = 0; i < n; i++) {
                int x = sc.nextInt();
                if (x == -1) break;
                scores.add(x);
            }
            
            for (int score : scores) {
                if (score >= 90 && score <= 100) {
                    System.out.println("Excellent");
                } else if (score >= 75 && score <= 89) {
                    System.out.println("Good");
                } else if (score >= 50 && score <= 74) {
                    System.out.println("Average");
                } else if (score >= 35 && score <= 49) {
                    System.out.println("Pass");
                } else if (score >= 0 && score <= 34) {
                    System.out.println("Fail");
                }
            }
        }
        
        sc.close();
    }
}
