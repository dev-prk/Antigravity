import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        try {
            int a = Integer.parseInt(scanner.nextLine().trim());
            int b = Integer.parseInt(scanner.nextLine().trim());
            int result = a / b;
            System.out.println(result);
        } catch (NumberFormatException e) {
            System.out.println("Invalid input");
        } catch (ArithmeticException e) {
            System.out.println("Cannot divide by zero");
        } finally {
            System.out.println("Operation Completed");
        }
    }
}
