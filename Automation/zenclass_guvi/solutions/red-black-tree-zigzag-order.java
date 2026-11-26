import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int value;
        int left;
        int right;
        
        Node(int value, int left, int right) {
            this.value = value;
            this.left = left;
            this.right = right;
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        Node[] nodes = new Node[n + 1];
        for (int i = 1; i <= n; i++) {
            String[] parts = br.readLine().trim().split("\\s+");
            int value = Integer.parseInt(parts[0]);
            int left = Integer.parseInt(parts[1]);
            int right = Integer.parseInt(parts[2]);
            nodes[i] = new Node(value, left, right);
        }
        
        if (n == 0) {
            return;
        }
        
        StringBuilder result = new StringBuilder();
        Queue<Integer> queue = new LinkedList<>();
        queue.offer(1);
        boolean leftToRight = true;
        
        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            List<Integer> levelValues = new ArrayList<>();
            
            for (int i = 0; i < levelSize; i++) {
                int nodeIndex = queue.poll();
                Node node = nodes[nodeIndex];
                levelValues.add(node.value);
                
                if (node.left != -1) {
                    queue.offer(node.left);
                }
                if (node.right != -1) {
                    queue.offer(node.right);
                }
            }
            
            if (!leftToRight) {
                Collections.reverse(levelValues);
            }
            
            for (int val : levelValues) {
                result.append(val).append(" ");
            }
            
            leftToRight = !leftToRight;
        }
        
        System.out.println(result.toString().trim());
    }
}
