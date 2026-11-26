import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int value;
        Node left;
        Node right;
        
        Node(int value) {
            this.value = value;
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        int N = Integer.parseInt(br.readLine().trim());
        
        Map<Integer, Node> nodeMap = new HashMap<>();
        Node root = null;
        
        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine().trim());
            int nodeValue = Integer.parseInt(st.nextToken());
            int leftValue = Integer.parseInt(st.nextToken());
            int rightValue = Integer.parseInt(st.nextToken());
            
            if (!nodeMap.containsKey(nodeValue)) {
                nodeMap.put(nodeValue, new Node(nodeValue));
            }
            
            Node node = nodeMap.get(nodeValue);
            
            if (leftValue != -1) {
                if (!nodeMap.containsKey(leftValue)) {
                    nodeMap.put(leftValue, new Node(leftValue));
                }
                node.left = nodeMap.get(leftValue);
            }
            
            if (rightValue != -1) {
                if (!nodeMap.containsKey(rightValue)) {
                    nodeMap.put(rightValue, new Node(rightValue));
                }
                node.right = nodeMap.get(rightValue);
            }
        }
        
        for (Map.Entry<Integer, Node> entry : nodeMap.entrySet()) {
            Node node = entry.getValue();
            if (node.left != null || node.right != null) {
                root = node;
                break;
            }
        }
        
        if (root == null && !nodeMap.isEmpty()) {
            root = nodeMap.values().iterator().next();
        }
        
        int K = Integer.parseInt(br.readLine().trim());
        
        if (search(root, K)) {
            System.out.println("Found");
        } else {
            System.out.println("Not Found");
        }
    }
    
    private static boolean search(Node root, int key) {
        if (root == null) {
            return false;
        }
        
        if (root.value == key) {
            return true;
        }
        
        return search(root.left, key) || search(root.right, key);
    }
}
