import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        
        if (s == null || s.isEmpty()) {
            System.out.println("No");
            return;
        }
        
        boolean isNumeric = true;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c < '0' || c > '9') {
                isNumeric = false;
                break;
            }
        }
        
        if (isNumeric) {
            System.out.println("Yes");
        } else {
            System.out.println("No");
        }
    }
}
