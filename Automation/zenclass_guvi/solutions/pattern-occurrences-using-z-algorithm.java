import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String text = br.readLine();
        String pattern = br.readLine();
        
        List<Integer> result = findPatternOccurrences(text, pattern);
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < result.size(); i++) {
            if (i > 0) sb.append(' ');
            sb.append(result.get(i));
        }
        System.out.println(sb.toString());
    }
    
    public static List<Integer> findPatternOccurrences(String text, String pattern) {
        List<Integer> indices = new ArrayList<>();
        if (pattern == null || pattern.isEmpty() || text.length() < pattern.length()) {
            return indices;
        }
        
        String combined = pattern + "#" + text;
        int[] z = computeZArray(combined);
        
        int patternLen = pattern.length();
        for (int i = 0; i < z.length; i++) {
            if (i >= patternLen + 1 && z[i] == patternLen) {
                indices.add(i - patternLen - 1);
            }
        }
        
        return indices;
    }
    
    public static int[] computeZArray(String s) {
        int n = s.length();
        int[] z = new int[n];
        int l = 0, r = 0;
        
        for (int i = 1; i < n; i++) {
            if (i <= r) {
                z[i] = Math.min(r - i + 1, z[i - l]);
            }
            
            while (i + z[i] < n && s.charAt(z[i]) == s.charAt(i + z[i])) {
                z[i]++;
            }
            
            if (i + z[i] - 1 > r) {
                l = i;
                r = i + z[i] - 1;
            }
        }
        
        return z;
    }
}
