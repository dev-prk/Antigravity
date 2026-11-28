import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) {
            System.out.println(-1);
            return;
        }
        s = s.trim();
        if (s.isEmpty()) {
            System.out.println(-1);
            return;
        }
        
        StringBuilder evenPosDigits = new StringBuilder();
        for (int i = 1; i < s.length(); i += 2) {
            evenPosDigits.append(s.charAt(i));
        }
        
        if (evenPosDigits.length() == 0) {
            System.out.println(-1);
            return;
        }
        
        String result = evenPosDigits.reverse().toString();
        
        // Remove leading zeros to interpret as integer
        int firstNonZero = 0;
        while (firstNonZero < result.length() - 1 && result.charAt(firstNonZero) == '0') {
            firstNonZero++;
        }
        
        System.out.println(result.substring(firstNonZero));
    }
}
