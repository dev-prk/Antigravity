import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String input = br.readLine().trim();
        
        if (input.startsWith("0")) {
            System.out.println("Not a Duck Number");
            return;
        }
        
        boolean hasZero = false;
        for (int i = 0; i < input.length(); i++) {
            if (input.charAt(i) == '0') {
                hasZero = true;
                break;
            }
        }
        
        if (hasZero) {
            System.out.println("Duck Number");
        } else {
            System.out.println("Not a Duck Number");
        }
    }
}
