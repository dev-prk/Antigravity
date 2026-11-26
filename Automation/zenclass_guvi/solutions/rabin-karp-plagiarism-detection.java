import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s1 = br.readLine();
        String s2 = br.readLine();
        
        if (isSubstring(s1, s2) || isSubstring(s2, s1)) {
            System.out.println("Plagiarism Detected");
        } else {
            System.out.println("No Plagiarism");
        }
    }

    private static boolean isSubstring(String s, String pattern) {
        int n = s.length();
        int m = pattern.length();
        
        if (m == 0) {
            return true;
        }
        if (m > n) {
            return false;
        }
        
        final int base = 256;
        final long mod = 1000000007;
        
        long patternHash = 0;
        long sWindowHash = 0;
        
        for (int i = 0; i < m; i++) {
            patternHash = (patternHash * base + pattern.charAt(i)) % mod;
            sWindowHash = (sWindowHash * base + s.charAt(i)) % mod;
        }
        
        long highPower = 1;
        for (int i = 0; i < m - 1; i++) {
            highPower = (highPower * base) % mod;
        }
        
        for (int i = 0; i <= n - m; i++) {
            if (patternHash == sWindowHash) {
                if (s.substring(i, i + m).equals(pattern)) {
                    return true;
                }
            }
            
            if (i < n - m) {
                sWindowHash = (sWindowHash - (long) s.charAt(i) * highPower) % mod;
                if (sWindowHash < 0) {
                    sWindowHash += mod;
                }
                sWindowHash = (sWindowHash * base + s.charAt(i + m)) % mod;
            }
        }
        
        return false;
    }
}
