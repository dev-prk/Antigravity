import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null || s.isEmpty()) {
            return;
        }
        int n = s.length();
        boolean[][] isPal = new boolean[n][n];
        for (int i = n - 1; i >= 0; i--) {
            for (int j = i; j < n; j++) {
                if (s.charAt(i) == s.charAt(j) && (j - i < 2 || isPal[i + 1][j - 1])) {
                    isPal[i][j] = true;
                }
            }
        }
        List<String> current = new ArrayList<>();
        backtrack(s, 0, isPal, current);
    }

    private static void backtrack(String s, int start, boolean[][] isPal, List<String> current) {
        if (start == s.length()) {
            System.out.println(String.join(" ", current));
            return;
        }
        for (int end = start; end < s.length(); end++) {
            if (isPal[start][end]) {
                current.add(s.substring(start, end + 1));
                backtrack(s, end + 1, isPal, current);
                current.remove(current.size() - 1);
            }
        }
    }
}
