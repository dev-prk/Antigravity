import java.util.*;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        sc.nextLine(); // consume newline
        
        String line = sc.nextLine().trim();
        if (n == 0 || line.isEmpty()) {
            System.out.println("Median: 0.0");
            return;
        }
        
        List<Double> numbers = Arrays.stream(line.split("\\s+"))
                .map(Double::parseDouble)
                .collect(Collectors.toList());
        
        Collections.sort(numbers);
        
        double median;
        int size = numbers.size();
        if (size % 2 == 1) {
            median = numbers.get(size / 2);
        } else {
            int mid1 = size / 2 - 1;
            int mid2 = size / 2;
            median = (numbers.get(mid1) + numbers.get(mid2)) / 2.0;
        }
        
        System.out.println("Median: " + median);
    }
}
