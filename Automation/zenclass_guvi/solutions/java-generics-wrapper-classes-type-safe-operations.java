import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        sc.nextLine();
        
        String line = sc.nextLine().trim();
        
        if (n <= 0 || line.isEmpty()) {
            System.out.println("Sum: 0.0");
            return;
        }
        
        String[] parts = line.split("\\s+");
        
        GenericSum<Double> sumCalculator = new GenericSum<>();
        List<Double> numbers = new ArrayList<>();
        
        for (String part : parts) {
            if (!part.isEmpty()) {
                numbers.add(Double.parseDouble(part));
            }
        }
        
        double result = sumCalculator.sum(numbers);
        System.out.println("Sum: " + result);
    }
}

class GenericSum<T extends Number> {
    public double sum(List<T> list) {
        if (list == null || list.isEmpty()) {
            return 0.0;
        }
        
        double total = 0.0;
        for (T item : list) {
            total += item.doubleValue();
        }
        return total;
    }
}
