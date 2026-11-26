import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String input = br.readLine();
        if (input == null || input.trim().isEmpty()) {
            System.out.println(0);
            return;
        }
        input = input.trim();
        double result = evaluate(input);
        System.out.println((int) result);
    }
    
    static double evaluate(String s) {
        s = s.replaceAll("\\s+", "");
        if (s.isEmpty()) return 0;
        
        Deque<Double> numbers = new ArrayDeque<>();
        Deque<Character> ops = new ArrayDeque<>();
        
        int i = 0;
        while (i < s.length()) {
            char c = s.charAt(i);
            
            if (c == '(') {
                ops.push(c);
                i++;
            } else if (c == ')') {
                while (!ops.isEmpty() && ops.peek() != '(') {
                    applyOp(numbers, ops.pop());
                }
                if (!ops.isEmpty() && ops.peek() == '(') {
                    ops.pop();
                }
                i++;
            } else if (isOperator(c)) {
                while (!ops.isEmpty() && ops.peek() != '(' && 
                       precedence(ops.peek()) >= precedence(c)) {
                    applyOp(numbers, ops.pop());
                }
                ops.push(c);
                i++;
            } else if (Character.isDigit(c) || c == '-') {
                int j = i;
                if (c == '-' && (j + 1 < s.length()) && 
                    (Character.isDigit(s.charAt(j + 1)) || s.charAt(j + 1) == '(')) {
                    j++;
                }
                while (j < s.length() && (Character.isDigit(s.charAt(j)) || s.charAt(j) == '.')) {
                    j++;
                }
                String numStr = s.substring(i, j);
                numbers.push(Double.parseDouble(numStr));
                i = j;
            } else {
                i++;
            }
        }
        
        while (!ops.isEmpty()) {
            applyOp(numbers, ops.pop());
        }
        
        return numbers.isEmpty() ? 0 : numbers.pop();
    }
    
    static boolean isOperator(char c) {
        return c == '+' || c == '-' || c == '*' || c == '/';
    }
    
    static int precedence(char op) {
        if (op == '+' || op == '-') return 1;
        if (op == '*' || op == '/') return 2;
        return 0;
    }
    
    static void applyOp(Deque<Double> numbers, char op) {
        if (numbers.size() < 2) return;
        double b = numbers.pop();
        double a = numbers.pop();
        switch (op) {
            case '+': numbers.push(a + b); break;
            case '-': numbers.push(a - b); break;
            case '*': numbers.push(a * b); break;
            case '/': numbers.push(b != 0 ? a / b : 0); break;
        }
    }
}
