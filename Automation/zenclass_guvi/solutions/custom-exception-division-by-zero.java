import java.util.Scanner;

class DivideByZeroException extends Exception {
    public DivideByZeroException(String message) {
        super(message);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        try {
            if (b == 0) {
                throw new DivideByZeroException("Cannot divide by zero");
            }
            int result = a / b;
            System.out.println("Result: " + result);
        } catch (DivideByZeroException e) {
            System.out.println(e.getMessage());
        }
    }
}
