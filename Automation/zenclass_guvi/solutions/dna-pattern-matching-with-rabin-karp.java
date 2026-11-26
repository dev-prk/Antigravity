import java.io.*;
import java.util.*;

public class Main {
    private static final long BASE = 911382123L;
    private static final long MOD = 1000000007L;
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String S = br.readLine();
        if (S == null) S = "";
        String P = br.readLine();
        if (P == null) P = "";
        
        List<Integer> result = rabinKarp(S, P);
        
        StringBuilder sb = new StringBuilder();
        if (result.isEmpty()) {
            sb.append(-1);
        } else {
            for (int i = 0; i < result.size(); i++) {
                if (i > 0) sb.append(' ');
                sb.append(result.get(i));
            }
        }
        System.out.print(sb.toString());
    }
    
    private static List<Integer> rabinKarp(String text, String pattern) {
        List<Integer> result = new ArrayList<>();
        int n = text.length();
        int m = pattern.length();
        
        if (m == 0) {
            for (int i = 0; i <= n; i++) {
                result.add(i);
            }
            return result;
        }
        
        if (n < m) {
            return result;
        }
        
        long patternHash = 0;
        long textHash = 0;
        long power = 1;
        
        for (int i = 0; i < m; i++) {
            patternHash = (patternHash * BASE + pattern.charAt(i)) % MOD;
            textHash = (textHash * BASE + text.charAt(i)) % MOD;
            power = (power * BASE) % MOD;
        }
        
        for (int i = 0; i <= n - m; i++) {
            if (patternHash == textHash) {
                if (checkMatch(text, pattern, i)) {
                    result.add(i);
                }
            }
            if (i < n - m) {
                textHash = (textHash * BASE - text.charAt(i) * power + text.charAt(i + m)) % MOD;
                if (textHash < 0) textHash += MOD;
            }
        }
        
        return result;
    }
    
    private static boolean checkMatch(String text, String pattern, int start) {
        for (int i = 0; i < pattern.length(); i++) {
            if (text.charAt(start + i) != pattern.charAt(i)) {
                return false;
            }
        }
        return true;
    }
}
