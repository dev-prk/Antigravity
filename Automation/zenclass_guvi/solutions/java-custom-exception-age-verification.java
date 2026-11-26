import java.util.Scanner;

class UnderageException extends Exception {
    public UnderageException(String message) {
        super(message);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int age = sc.nextInt();
        try {
            if (age < 18) {
                throw new UnderageException("Age " + age + " is below the legal age limit.");
            }
            System.out.println("Age verification successful.");
        } catch (UnderageException e) {
            System.out.println("UnderageException: " + e.getMessage());
        }
    }
}
