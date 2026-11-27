import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        long oddSum = 0, evenSum = 0;
        
        while (sc.hasNextInt()) {
            int num = sc.nextInt();
            if (num == -1) break;
            
            if (num % 2 == 0) {
                evenSum += num;
            } else {
                oddSum += num;
            }
        }
        
        if (oddSum > evenSum) {
            System.out.println("Odd Sum Greater");
        } else if (evenSum > oddSum) {
            System.out.println("Even Sum Greater");
        } else {
            System.out.println("Equal");
        }
        
        sc.close();
    }
}
