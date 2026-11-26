import java.util.*;
import java.util.function.Function;

@FunctionalInterface
interface StringFunction {
    String apply(String s);
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) {
            return;
        }
        int n = sc.nextInt();
        sc.nextLine(); // Consume the newline
        
        List<String> strings = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            if (sc.hasNextLine()) {
                String line = sc.nextLine();
                strings.add(line);
            }
        }
        
        // Use lambda expression with toUpperCase and sort in reverse alphabetical order
        StringFunction toUpper = s -> s.toUpperCase();
        strings.replaceAll(s -> toUpper.apply(s));
        
        // Sort in reverse alphabetical order
        strings.sort((a, b) -> b.compareTo(a));
        
        // Print each string on a new line
        for (String s : strings) {
            System.out.println(s);
        }
    }
}
