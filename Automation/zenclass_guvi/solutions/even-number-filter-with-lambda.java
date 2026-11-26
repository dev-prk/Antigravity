import java.util.*;
import java.util.function.Predicate;

@FunctionalInterface
interface Condition {
    boolean test(int value);
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextInt()) {
            sc.close();
            return;
        }
        
        int n = sc.nextInt();
        int[] arr = new int[n];
        
        for (int i = 0; i < n; i++) {
            if (sc.hasNextInt()) {
                arr[i] = sc.nextInt();
            } else {
                sc.close();
                return;
            }
        }
        
        sc.close();
        
        Condition isOdd = (x) -> x % 2 != 0;
        
        for (int num : arr) {
            if (isOdd.test(num)) {
                System.out.println(num);
            }
        }
    }
}
