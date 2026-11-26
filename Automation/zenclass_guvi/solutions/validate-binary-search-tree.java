import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int val;
        int left;
        int right;
        
        Node(int val, int left, int right) {
            this.val = val;
            this.left = left;
            this.right = right;
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        Node[] nodes = new Node[n];
        for (int i = 0; i < n; i++) {
            String[] parts = br.readLine().trim().split("\\s+");
            int val = Integer.parseInt(parts[0]);
            int left = Integer.parseInt(parts[1]);
            int right = Integer.parseInt(parts[2]);
            nodes[i] = new Node(val, left, right);
        }
        
        boolean result = isValidBST(nodes, 0, Long.MIN_VALUE, Long.MAX_VALUE);
        System.out.println(result ? "true" : "false");
    }
    
    static boolean isValidBST(Node[] nodes, int idx, long min, long max) {
        if (idx == -1) return true;
        
        Node node = nodes[idx];
        
        if (node.val <= min || node.val >= max) {
            return false;
        }
        
        return isValidBST(nodes, node.left, min, node.val) &&
               isValidBST(nodes, node.right, node.val, max);
    }
}
