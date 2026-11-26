import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String num = br.readLine();
        if (num == null || num.isEmpty()) {
            System.out.println("0");
            return;
        }
        int k = Integer.parseInt(br.readLine().trim());
        
        if (k <= 0) {
            System.out.println(removeLeadingZeros(num));
            return;
        }
        
        if (k >= num.length()) {
            System.out.println("0");
            return;
        }
        
        char[] stack = new char[num.length()];
        int top = -1;
        
        for (int i = 0; i < num.length(); i++) {
            char c = num.charAt(i);
            while (k > 0 && top >= 0 && stack[top] > c) {
                top--;
                k--;
            }
            stack[++top] = c;
        }
        
        // Remove remaining k digits from the end
        top -= k;
        
        // Build result
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i <= top; i++) {
            sb.append(stack[i]);
        }
        
        String result = removeLeadingZeros(sb.toString());
        System.out.println(result.isEmpty() ? "0" : result);
    }
    
    private static String removeLeadingZeros(String s) {
        int i = 0;
        while (i < s.length() && s.charAt(i) == '0') {
            i++;
        }
        if (i == s.length()) return "0";
        return s.substring(i);
    }
}
