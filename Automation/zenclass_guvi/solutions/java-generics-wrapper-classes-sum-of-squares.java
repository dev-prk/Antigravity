import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        sc.nextLine();
        
        double sum = 0.0;
        if (n > 0) {
            String line = sc.nextLine().trim();
            if (!line.isEmpty()) {
                sum = Arrays.stream(line.split("\\s+"))
                           .mapToDouble(Double::parseDouble)
                           .map(x -> x * x)
                           .sum();
            }
        }
        
        System.out.println("Sum of Squares: " + sum);
    }
}
