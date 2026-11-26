import java.util.Scanner;

class InvalidAgeException extends Exception {
    public InvalidAgeException(String message) {
        super(message);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        int age = Integer.parseInt(scanner.nextLine().trim());
        
        try {
            if (age < 18) {
                throw new InvalidAgeException("Age must be 18 or older");
            }
            System.out.println("Age is valid");
        } catch (InvalidAgeException e) {
            System.out.println(e.getMessage());
        }
    }
}
