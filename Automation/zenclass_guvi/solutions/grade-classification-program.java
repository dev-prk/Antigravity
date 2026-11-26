import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        int n = scanner.nextInt();
        
        for (int i = 0; i < n; i++) {
            int score = scanner.nextInt();
            
            if (score >= 90 && score <= 100) {
                System.out.println("Excellent");
            } else if (score >= 75 && score < 90) {
                System.out.println("Good");
            } else if (score >= 50 && score < 75) {
                System.out.println("Average");
            } else if (score >= 35 && score < 50) {
                System.out.println("Pass");
            } else if (score >= 0 && score < 35) {
                System.out.println("Fail");
            }
        }
    }
}
