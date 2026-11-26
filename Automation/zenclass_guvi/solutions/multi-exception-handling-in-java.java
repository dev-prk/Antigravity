import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        try {
            int dividend = Integer.parseInt(scanner.nextLine().trim());
            int divisor = Integer.parseInt(scanner.nextLine().trim());
            int result = dividend / divisor;
            System.out.println("Result: " + result);
        } catch (ArithmeticException e) {
            System.out.println("ArithmeticException: Division by zero is not allowed.");
        } catch (NumberFormatException e) {
            System.out.println("NumberFormatException: Invalid input. Please enter integers only.");
        }
    }
}
