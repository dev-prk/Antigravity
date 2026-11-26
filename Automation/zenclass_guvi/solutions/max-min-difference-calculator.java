import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        if (n <= 0) {
            System.out.println("Difference: 0.0");
            return;
        }
        
        sc.nextLine();
        String line = sc.nextLine().trim();
        if (line.isEmpty()) {
            System.out.println("Difference: 0.0");
            return;
        }
        
        String[] parts = line.split("\\s+");
        List<Double> list = new ArrayList<>();
        for (String part : parts) {
            if (!part.isEmpty()) {
                list.add(Double.parseDouble(part));
            }
        }
        
        if (list.isEmpty()) {
            System.out.println("Difference: 0.0");
            return;
        }
        
        Double max = list.get(0);
        Double min = list.get(0);
        for (Double num : list) {
            if (num > max) max = num;
            if (num < min) min = num;
        }
        
        double diff = max - min;
        System.out.println("Difference: " + diff);
    }
}
