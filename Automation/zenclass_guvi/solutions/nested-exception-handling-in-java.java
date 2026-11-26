import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int sum = 0;
        
        while (scanner.hasNext()) {
            try {
                try {
                    int num = Integer.parseInt(scanner.next());
                    sum += num;
                } catch (NumberFormatException e) {
                    // Skip non-integer values
                }
            } catch (Exception e) {
                // Handle any other exceptions
            }
        }
        
        System.out.println("Sum of entered integers: " + sum);
        scanner.close();
    }
}
