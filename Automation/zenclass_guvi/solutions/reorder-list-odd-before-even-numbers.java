import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        int n = scanner.nextInt();
        scanner.nextLine(); // Consume the newline
        
        List<Integer> original = new ArrayList<>();
        String line = scanner.nextLine();
        String[] parts = line.split(" ");
        for (String part : parts) {
            if (!part.isEmpty()) {
                original.add(Integer.parseInt(part));
            }
        }
        
        List<Integer> odds = new ArrayList<>();
        List<Integer> evens = new ArrayList<>();
        
        for (Integer num : original) {
            if (num % 2 != 0) {
                odds.add(num);
            } else {
                evens.add(num);
            }
        }
        
        // Combine the two lists
        List<Integer> result = new ArrayList<>();
        result.addAll(odds);
        result.addAll(evens);
        
        // Print the result using iterator
        Iterator<Integer> iterator = result.iterator();
        StringBuilder sb = new StringBuilder();
        while (iterator.hasNext()) {
            sb.append(iterator.next());
            if (iterator.hasNext()) {
                sb.append(" ");
            }
        }
        sb.append(" "); // Add trailing space
        System.out.print(sb.toString());
    }
}
