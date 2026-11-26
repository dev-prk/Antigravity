import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine().trim();
        int n = s.length();
        
        if (n <= 1) {
            System.out.println("NO");
            return;
        }
        
        int[] pi = new int[n];
        pi[0] = 0;
        
        for (int i = 1; i < n; i++) {
            int j = pi[i - 1];
            while (j > 0 && s.charAt(i) != s.charAt(j)) {
                j = pi[j - 1];
            }
            if (s.charAt(i) == s.charAt(j)) {
                j++;
            }
            pi[i] = j;
        }
        
        int len = pi[n - 1];
        if (len > 0 && n % (n - len) == 0) {
            System.out.println("YES");
        } else {
            System.out.println("NO");
        }
    }
}
