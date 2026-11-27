import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String input = br.readLine();
        
        StringBuilder sb = new StringBuilder(input);
        String reversed = sb.reverse().toString();
        
        String upper = input.toUpperCase();
        
        char nonRepeated = findFirstNonRepeated(input);
        
        System.out.println(reversed);
        System.out.println(upper);
        
        if (nonRepeated == '\0') {
            System.out.println("No non-repeated character found.");
        } else {
            System.out.println(nonRepeated);
        }
    }
    
    private static char findFirstNonRepeated(String s) {
        int[] count = new int[256];
        for (int i = 0; i < s.length(); i++) {
            count[s.charAt(i)]++;
        }
        for (int i = 0; i < s.length(); i++) {
            if (count[s.charAt(i)] == 1) {
                return s.charAt(i);
            }
        }
        return '\0';
    }
}
