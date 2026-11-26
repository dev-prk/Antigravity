import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        //..... YOUR CODE STARTS HERE .....
        
        Scanner scanner = new Scanner(System.in);
        
        // Read the two string inputs
        String input1 = scanner.nextLine();
        String input2 = scanner.nextLine();
        
        // Parse the strings to integers using Integer.parseInt()
        int num1 = Integer.parseInt(input1);
        int num2 = Integer.parseInt(input2);
        
        // Perform arithmetic operations
        int sum = num1 + num2;
        int difference = num1 - num2;
        int product = num1 * num2;
        int quotient = num1 / num2;  // Integer division
        
        // Print the results
        System.out.println("Addition: " + sum);
        System.out.println("Subtraction: " + difference);
        System.out.println("Multiplication: " + product);
        System.out.println("Division: " + quotient);
        
        //..... YOUR CODE ENDS HERE .....
    }
}
