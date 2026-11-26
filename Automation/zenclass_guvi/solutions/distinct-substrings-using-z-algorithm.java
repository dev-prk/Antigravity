import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int T = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();
        while (T-- > 0) {
            String S = br.readLine().trim();
            sb.append(countDistinctSubstrings(S)).append('\n');
        }
        System.out.print(sb.toString());
    }
    
    private static int countDistinctSubstrings(String S) {
        int n = S.length();
        if (n == 0) return 0;
        
        String T = S + "$" + new StringBuilder(S).reverse().toString();
        int[] z = computeZ(T);
        
        HashSet<String> distinct = new HashSet<>();
        for (int i = 0; i < n; i++) {
            for (int j = 1; j <= n - i; j++) {
                distinct.add(S.substring(i, i + j));
            }
        }
        
        return distinct.size();
    }
    
    private static int[] computeZ(String s) {
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
