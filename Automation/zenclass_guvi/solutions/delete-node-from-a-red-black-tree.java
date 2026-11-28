import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int key;
        char color;
        Node left, right, parent;
        
        Node(int key, char color) {
            this.key = key;
            this.color = color;
        }
    }
    
    static final char RED = 'R';
    static final char BLACK = 'B';
    
    static Node root;
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int N = sc.nextInt();
        int[] keys = new int[N];
        for (int i = 0; i < N; i++) {
            keys[i] = sc.nextInt();
        }
        
        char[] colors = new char[N];
        for (int i = 0; i < N; i++) {
            colors[i] = sc.next().charAt(0);
        }
        
        int K = sc.nextInt();
        
        if (N > 0) {
            Node[] nodes = new Node[N];
            for (int i = 0; i < N; i++) {
                nodes[i] = new Node(keys[i], colors[i]);
            }
            
            for (int i = 0; i < N; i++) {
                Node node = nodes[i];
                if (i == 0) {
                    root = node;
                } else {
                    node.parent = nodes[(i - 1) / 2];
                    Node parent = node.parent;
                    if (parent.left == null) {
                        parent.left = node;
                    } else {
                        parent.right = node;
                    }
                }
            }
        }
        
        if (root != null) {
            root = deleteNode(root, K);
        }
        
        List<Integer> levelOrder = getLevelOrder();
        List<Character> colorsList = getColors();
        
        for (int i = 0; i < levelOrder.size(); i++) {
            System.out.print(levelOrder.get(i));
            if (i < levelOrder.size() - 1) {
                System.out.print(" ");
            }
        }
        System.out.println();
        
        for (int i = 0; i < colorsList.size(); i++) {
            System.out.print(colorsList.get(i));
            if (i < colorsList.size() - 1) {
                System.out.print(" ");
            }
        }
        System.out.println();
    }
    
    static Node deleteNode(Node root, int key) {
        Node node = findMin(root, key);
        if (node == null) {
            return root;
        }
        return deleteHelper(root, key);
    }
    
    static Node findMin(Node root, int key) {
        if (root == null) return null;
        if (root.key == key) return root;
        Node left = findMin(root.left, key);
        if (left != null) return left;
        return findMin(root.right, key);
    }
    
    static Node deleteHelper(Node root, int key) {
        if (root == null) return null;
        
        if (key < root.key) {
            root.left = deleteHelper(root.left, key);
            if (root.left != null) root.left.parent = root;
        } else if (key > root.key) {
            root.right = deleteHelper(root.right, key);
            if (root.right != null) root.right.parent = root;
        } else {
            if (root.left == null && root.right == null) {
                return null;
            } else if (root.left == null) {
                return root.right;
            } else if (root.right == null) {
                return root.left;
            } else {
                Node successor = getSuccessor(root);
                root.key = successor.key;
                root.color = successor.color;
                root.right = deleteHelper(root.right, successor.key);
                if (root.right != null) root.right.parent = root;
            }
        }
        return root;
    }
    
    static Node getSuccessor(Node node) {
        Node current = node.right;
        while (current.left != null) {
            current = current.left;
        }
        return current;
    }
    
    static List<Integer> getLevelOrder() {
        List<Integer> result = new ArrayList<>();
        if (root == null) return result;
        
        Queue<Node> queue = new LinkedList<>();
        queue.offer(root);
        
        while (!queue.isEmpty()) {
            Node node = queue.poll();
            if (node != null) {
                result.add(node.key);
                queue.offer(node.left);
                queue.offer(node.right);
            }
        }
        
        return result;
    }
    
    static List<Character> getColors() {
        List<Character> result = new ArrayList<>();
        if (root == null) return result;
        
        Queue<Node> queue = new LinkedList<>();
        queue.offer(root);
        
        while (!queue.isEmpty()) {
            Node node = queue.poll();
            if (node != null) {
                result.add(node.color);
                queue.offer(node.left);
                queue.offer(node.right);
            }
        }
        
        return result;
    }
}
