import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        
        if (s == null) {
            System.out.println("Not Palindrome");
            return;
        }
        
        String trimmed = s.trim();
        if (trimmed.isEmpty()) {
            System.out.println("Palindrome");
            return;
        }
        
        String reversed = new StringBuffer(trimmed).reverse().toString();
        
        if (trimmed.equals(reversed)) {
            System.out.println("Palindrome");
        } else {
            System.out.println("Not Palindrome");
        }
    }
}
