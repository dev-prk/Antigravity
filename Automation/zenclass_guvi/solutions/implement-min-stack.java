import java.io.*;
import java.util.*;

public class Main {
    static class MinStack {
        private Stack<Integer> stack;
        private Stack<Integer> minStack;
        
        public MinStack() {
            stack = new Stack<>();
            minStack = new Stack<>();
        }
        
        public void push(int x) {
            stack.push(x);
            if (minStack.isEmpty() || x <= minStack.peek()) {
                minStack.push(x);
            }
        }
        
        public Integer pop() {
            if (stack.isEmpty()) {
                return null;
            }
            int val = stack.pop();
            if (val == minStack.peek()) {
                minStack.pop();
            }
            return val;
        }
        
        public Integer getMin() {
            if (minStack.isEmpty()) {
                return null;
            }
            return minStack.peek();
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        MinStack ms = new MinStack();
        String line;
        
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (line.equals("exit")) {
                break;
            }
            
            String[] parts = line.split("\\s+");
            
            if (parts[0].equals("push") && parts.length == 2) {
                int x = Integer.parseInt(parts[1]);
                ms.push(x);
            } else if (parts[0].equals("pop")) {
                ms.pop();
            } else if (parts[0].equals("getMin")) {
                Integer min = ms.getMin();
                if (min != null) {
                    System.out.println(min);
                }
            }
        }
    }
}
