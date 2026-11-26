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
        try {
            if (age < 18) {
                throw new InvalidAgeException("Invalid Age: must be 18 or above");
            }
            System.out.println("Eligible to Vote");
        } catch (InvalidAgeException e) {
            System.out.println(e.getMessage());
        }
    }
}
