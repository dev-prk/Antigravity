import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String className = br.readLine();
        
        if (className == null || className.isEmpty()) {
            System.out.println("Invalid Naming");
            return;
        }
        
        if (Character.isUpperCase(className.charAt(0))) {
            System.out.println("Valid Naming");
        } else {
            System.out.println("Invalid Naming");
        }
    }
}
