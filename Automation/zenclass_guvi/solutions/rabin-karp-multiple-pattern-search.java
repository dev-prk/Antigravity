import java.io.*;
import java.util.*;

public class Main {
    private static final long BASE = 256L;
    private static final long MOD = 1000000007L;
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        String[] patterns = new String[n];
        for (int i = 0; i < n; i++) {
            patterns[i] = br.readLine();
        }
        
        String text = br.readLine();
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            String pattern = patterns[i];
            List<Integer> positions = rabinKarpMultiPattern(pattern, text);
            if (positions.isEmpty()) {
                sb.append("-1\n");
            } else {
                for (int j = 0; j < positions.size(); j++) {
                    if (j > 0) sb.append(' ');
                    sb.append(positions.get(j));
                }
                sb.append('\n');
            }
        }
        System.out.print(sb.toString());
    }
    
    public static List<Integer> rabinKarpMultiPattern(String pattern, String text) {
        List<Integer> result = new ArrayList<>();
        int m = pattern.length();
        int n = text.length();
        
        if (m > n || m == 0) {
            return result;
        }
        
        long patternHash = 0;
        long textHash = 0;
        long h = 1;
        
        for (int i = 0; i < m; i++) {
            patternHash = (patternHash * BASE + pattern.charAt(i)) % MOD;
            textHash = (textHash * BASE + text.charAt(i)) % MOD;
        }
        
        for (int i = 0; i < m - 1; i++) {
            h = (h * BASE) % MOD;
        }
        
        for (int i = 0; i <= n - m; i++) {
            if (patternHash == textHash) {
                if (text.substring(i, i + m).equals(pattern)) {
                    result.add(i);
                }
            }
            
            if (i < n - m) {
                textHash = (textHash + MOD - (h * text.charAt(i)) % MOD) % MOD;
                textHash = (textHash * BASE + text.charAt(i + m)) % MOD;
            }
        }
        
        return result;
    }
}
