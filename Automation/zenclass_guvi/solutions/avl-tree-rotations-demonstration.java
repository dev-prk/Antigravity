import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int key, height;
        Node left, right;
        
        Node(int key) {
            this.key = key;
            this.height = 1;
        }
    }
    
    static int height(Node n) {
        return n == null ? 0 : n.height;
    }
    
    static int getBalance(Node n) {
        return n == null ? 0 : height(n.left) - height(n.right);
    }
    
    static Node rightRotate(Node y) {
        Node x = y.left;
        Node T2 = x.right;
        
        x.right = y;
        y.left = T2;
        
        y.height = Math.max(height(y.left), height(y.right)) + 1;
        x.height = Math.max(height(x.left), height(x.right)) + 1;
        
        return x;
    }
    
    static Node leftRotate(Node x) {
        Node y = x.right;
        Node T2 = y.left;
        
        y.left = x;
        x.right = T2;
        
        x.height = Math.max(height(x.left), height(x.right)) + 1;
        y.height = Math.max(height(y.left), height(y.right)) + 1;
        
        return y;
    }
    
    static Node insert(Node node, int key, List<String> rotations) {
        if (node == null)
            return new Node(key);
        
        if (key < node.key)
            node.left = insert(node.left, key, rotations);
        else if (key > node.key)
            node.right = insert(node.right, key, rotations);
        else
            return node;
        
        node.height = 1 + Math.max(height(node.left), height(node.right));
        
        int balance = getBalance(node);
        
        // LL case (Left-Left)
        if (balance > 1 && key < node.left.key) {
            rotations.add("LL Rotation at node " + node.key);
            return rightRotate(node);
        }
        
        // RR case (Right-Right)
        if (balance < -1 && key > node.right.key) {
            rotations.add("RR Rotation at node " + node.key);
            return leftRotate(node);
        }
        
        // LR case (Left-Right)
        if (balance > 1 && key > node.left.key) {
            node.left = leftRotate(node.left);
            rotations.add("LR Rotation at node " + node.key);
            return rightRotate(node);
        }
        
        // RL case (Right-Left)
        if (balance < -1 && key < node.right.key) {
            node.right = rightRotate(node.right);
            rotations.add("RL Rotation at node " + node.key);
            return leftRotate(node);
        }
        
        return node;
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        Node root = null;
        List<String> rotations = new ArrayList<>();
        
        if (n > 0) {
            String[] parts = br.readLine().trim().split("\\s+");
            for (int i = 0; i < n; i++) {
                int key = Integer.parseInt(parts[i]);
                root = insert(root, key, rotations);
            }
        }
        
        for (String r : rotations) {
            System.out.println(r);
        }
    }
}
