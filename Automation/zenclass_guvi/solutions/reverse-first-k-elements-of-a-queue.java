import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] queueStr = br.readLine().trim().split("\\s+");
        int K = Integer.parseInt(br.readLine().trim());
        
        Queue<Integer> queue = new LinkedList<>();
        for (String s : queueStr) {
            queue.offer(Integer.parseInt(s));
        }
        
        Stack<Integer> stack = new Stack<>();
        int n = queue.size();
        
        // Handle edge cases
        if (K < 0) K = 0;
        if (K > n) K = n;
        
        // Push first K elements to stack
        for (int i = 0; i < K; i++) {
            stack.push(queue.poll());
        }
        
        // Pop from stack and add to queue
        while (!stack.isEmpty()) {
            queue.offer(stack.pop());
        }
        
        // Move remaining elements to front
        int remaining = n - K;
        for (int i = 0; i < remaining; i++) {
            queue.offer(queue.poll());
        }
        
        // Print result with trailing space
        StringBuilder sb = new StringBuilder();
        while (!queue.isEmpty()) {
            sb.append(queue.poll()).append(" ");
        }
        System.out.print(sb.toString());
    }
}
