import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line1 = br.readLine();
        String line2 = br.readLine();
        
        if (line1 == null || line2 == null || line1.trim().isEmpty() || line2.trim().isEmpty()) {
            System.out.println("false");
            return;
        }
        
        String[] parts1 = line1.trim().split("\\s+");
        String[] parts2 = line2.trim().split("\\s+");
        
        int[] input = new int[parts1.length];
        int[] target = new int[parts2.length];
        
        for (int i = 0; i < parts1.length; i++) {
            input[i] = Integer.parseInt(parts1[i]);
        }
        for (int i = 0; i < parts2.length; i++) {
            target[i] = Integer.parseInt(parts2[i]);
        }
        
        System.out.println(isStackPermutation(input, target));
    }
    
    static String isStackPermutation(int[] input, int[] target) {
        Stack<Integer> stack = new Stack<>();
        int j = 0;
        
        for (int i = 0; i < input.length; i++) {
            stack.push(input[i]);
            
            while (!stack.isEmpty() && j < target.length && stack.peek() == target[j]) {
                stack.pop();
                j++;
            }
        }
        
        return stack.isEmpty() ? "true" : "false";
    }
}
