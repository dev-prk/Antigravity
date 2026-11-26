import java.util.Scanner;

// Custom Exception Class
class InvalidUsernameException extends Exception {
    public InvalidUsernameException(String message) {
        super(message);
    }
}

// UserManager Class
class UserManager {
    public void registerUser(String username) throws InvalidUsernameException {
        if (username == null || username.length() < 5) {
            throw new InvalidUsernameException("Too short.");
        }
        
        for (char c : username.toCharArray()) {
            if (!Character.isLetterOrDigit(c)) {
                throw new InvalidUsernameException("Contains non-alphanumeric characters.");
            }
        }
    }
}

// Main Class
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String username = sc.nextLine();
        if (username != null) {
            username = username.trim();
        }
        UserManager manager = new UserManager();
        
        try {
            manager.registerUser(username);
            System.out.println("Username registered successfully.");
        } catch (InvalidUsernameException e) {
            System.out.println("Invalid username: " + e.getMessage());
        }
    }
}
