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
    
    static int height(Node node) {
        return node == null ? 0 : node.height;
    }
    
    static int getBalance(Node node) {
        return node == null ? 0 : height(node.left) - height(node.right);
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
    
    static Node insert(Node node, int key) {
        if (node == null)
            return new Node(key);
        
        if (key < node.key)
            node.left = insert(node.left, key);
        else if (key > node.key)
            node.right = insert(node.right, key);
        else
            return node;
        
        node.height = 1 + Math.max(height(node.left), height(node.right));
        
        int balance = getBalance(node);
        
        // Left Left Case
        if (balance > 1 && key < node.left.key)
            return rightRotate(node);
        
        // Right Right Case
        if (balance < -1 && key > node.right.key)
            return leftRotate(node);
        
        // Left Right Case
        if (balance > 1 && key > node.left.key) {
            node.left = leftRotate(node.left);
            return rightRotate(node);
        }
        
        // Right Left Case
        if (balance < -1 && key < node.right.key) {
            node.right = rightRotate(node.right);
            return leftRotate(node);
        }
        
        return node;
    }
    
    static void preOrder(Node node, List<Integer> result) {
        if (node != null) {
            result.add(node.key);
            preOrder(node.left, result);
            preOrder(node.right, result);
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        String nStr = br.readLine();
        if (nStr == null || nStr.trim().isEmpty()) {
            System.out.println("");
            return;
        }
        
        int n = Integer.parseInt(nStr.trim());
        
        if (n == 0) {
            System.out.println("");
            return;
        }
        
        StringTokenizer st = new StringTokenizer(br.readLine());
        Node root = null;
        
        for (int i = 0; i < n && st.hasMoreTokens(); i++) {
            int key = Integer.parseInt(st.nextToken());
            root = insert(root, key);
        }
        
        List<Integer> result = new ArrayList<>();
        preOrder(root, result);
        
        System.out.println(String.join(" ", result.stream()
            .map(String::valueOf)
            .toArray(String[]::new)));
    }
}
