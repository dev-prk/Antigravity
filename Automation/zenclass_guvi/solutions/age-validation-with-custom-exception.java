import java.util.Scanner;

class InvalidAgeException extends Exception {
    public InvalidAgeException(String message) {
        super(message);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int age = sc.nextInt();
        sc.close();
        
        try {
            if (age < 18) {
                throw new InvalidAgeException("Age must be at least 18");
            }
            System.out.println("Valid Age");
        } catch (InvalidAgeException e) {
            System.out.println(e.getMessage());
        }
    }
}
