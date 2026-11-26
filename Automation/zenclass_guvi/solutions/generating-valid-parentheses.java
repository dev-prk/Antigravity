import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.trim().isEmpty()) {
            System.out.println("[]");
            return;
        }
        int n = Integer.parseInt(line.trim());
        if (n < 0) {
            System.out.println("[]");
            return;
        }
        List<String> result = new ArrayList<>();
        generateParentheses(n, 0, 0, new StringBuilder(), result);
        Collections.sort(result);
        System.out.println(result);
    }
    
    private static void generateParentheses(int n, int open, int close, StringBuilder current, List<String> result) {
        if (current.length() == 2 * n) {
            result.add(current.toString());
            return;
        }
        if (open < n) {
            current.append('(');
            generateParentheses(n, open + 1, close, current, result);
            current.deleteCharAt(current.length() - 1);
        }
        if (close < open) {
            current.append(')');
            generateParentheses(n, open, close + 1, current, result);
            current.deleteCharAt(current.length() - 1);
        }
    }
}
