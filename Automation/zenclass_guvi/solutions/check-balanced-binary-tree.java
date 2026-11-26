import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int val;
        Node left, right;
        Node(int val) { this.val = val; }
    }
    
    static class Result {
        boolean balanced;
        int height;
        Result(boolean balanced, int height) {
            this.balanced = balanced;
            this.height = height;
        }
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) {
            System.out.println("true");
            return;
        }
        int n = Integer.parseInt(line.trim());
        if (n == 0) {
            System.out.println("true");
            return;
        }
        
        Map<Integer, Node> nodeMap = new HashMap<>();
        Map<Integer, Integer> parentMap = new HashMap<>();
        Set<Integer> children = new HashSet<>();
        
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int val = Integer.parseInt(st.nextToken());
            int leftVal = Integer.parseInt(st.nextToken());
            int rightVal = Integer.parseInt(st.nextToken());
            
            Node node = nodeMap.get(val);
            if (node == null) {
                node = new Node(val);
                nodeMap.put(val, node);
            }
            
            if (leftVal != -1) {
                Node leftNode = nodeMap.get(leftVal);
                if (leftNode == null) {
                    leftNode = new Node(leftVal);
                    nodeMap.put(leftVal, leftNode);
                }
                node.left = leftNode;
                children.add(leftVal);
                parentMap.put(leftVal, val);
            }
            
            if (rightVal != -1) {
                Node rightNode = nodeMap.get(rightVal);
                if (rightNode == null) {
                    rightNode = new Node(rightVal);
                    nodeMap.put(rightVal, rightNode);
                }
                node.right = rightNode;
                children.add(rightVal);
                parentMap.put(rightVal, val);
            }
        }
        
        int rootVal = -1;
        for (int val : nodeMap.keySet()) {
            if (!children.contains(val)) {
                rootVal = val;
                break;
            }
        }
        
        if (rootVal == -1) {
            System.out.println("true");
            return;
        }
        
        Node root = nodeMap.get(rootVal);
        Result res = checkBalanced(root);
        System.out.println(res.balanced ? "true" : "false");
    }
    
    static Result checkBalanced(Node root) {
        if (root == null) {
            return new Result(true, 0);
        }
        
        Result left = checkBalanced(root.left);
        Result right = checkBalanced(root.right);
        
        boolean balanced = left.balanced && right.balanced && 
                          Math.abs(left.height - right.height) <= 1;
        int height = 1 + Math.max(left.height, right.height);
        
        return new Result(balanced, height);
    }
}
