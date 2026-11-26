import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        // Read double and float values
        double d = sc.nextDouble();
        float f = sc.nextFloat();
        
        // Convert using wrapper class methods (truncation)
        int fromDouble = (int) d;
        int fromFloat = (int) f;
        
        // Output results
        System.out.println("Converted Integer from Double: " + fromDouble);
        System.out.println("Converted Integer from Float: " + fromFloat);
        System.out.println("Note: Data was truncated, not rounded.");
        
        sc.close();
    }
}
