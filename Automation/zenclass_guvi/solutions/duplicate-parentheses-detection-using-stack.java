import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null || s.length() == 0) {
            System.out.println(false);
            return;
        }
        Deque<Character> st = new ArrayDeque<>();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == ')') {
                if (st.isEmpty()) {
                    System.out.println(true);
                    return;
                }
                int count = 0;
                while (!st.isEmpty() && st.peek() != '(') {
                    st.pop();
                    count++;
                }
                if (st.isEmpty()) {
                    System.out.println(true);
                    return;
                }
                st.pop();
                if (count == 0) {
                    System.out.println(true);
                    return;
                }
            } else if (c == '(' || c != ' ' && c != '\t' && c != '\n') {
                st.push(c);
            }
        }
        System.out.println(false);
    }
}
