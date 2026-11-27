import java.io.*;
import java.util.*;

public class Main {
    static final int RED = 0;
    static final int BLACK = 1;
    
    static class Node {
        int data, color;
        Node left, right, parent;
        
        Node(int data) {
            this.data = data;
            this.color = RED;
            this.left = null;
            this.right = null;
            this.parent = null;
        }
    }
    
    static class RedBlackTree {
        Node root;
        Node NIL;
        
        RedBlackTree() {
            NIL = new Node(-1);
            NIL.color = BLACK;
            NIL.left = NIL.right = NIL.parent = NIL;
            root = NIL;
        }
        
        void leftRotate(Node x) {
            Node y = x.right;
            x.right = y.left;
            if (y.left != NIL) y.left.parent = x;
            y.parent = x.parent;
            if (x.parent == NIL) root = y;
            else if (x == x.parent.left) x.parent.left = y;
            else x.parent.right = y;
            y.left = x;
            x.parent = y;
        }
        
        void rightRotate(Node y) {
            Node x = y.left;
            y.left = x.right;
            if (x.right != NIL) x.right.parent = y;
            x.parent = y.parent;
            if (y.parent == NIL) root = x;
            else if (y == y.parent.right) y.parent.right = x;
            else y.parent.left = x;
            x.right = y;
            y.parent = x;
        }
        
        void insert(int data) {
            Node node = new Node(data);
            node.left = node.right = node.parent = NIL;
            node.color = RED;
            
            Node y = NIL;
            Node x = root;
            
            while (x != NIL) {
                y = x;
                if (node.data < x.data) x = x.left;
                else x = x.right;
            }
            
            node.parent = y;
            if (y == NIL) root = node;
            else if (node.data < y.data) y.left = node;
            else y.right = node;
            
            insertFixup(node);
        }
        
        void insertFixup(Node node) {
            while (node.parent.color == RED) {
                if (node.parent == node.parent.parent.left) {
                    Node y = node.parent.parent.right;
                    if (y.color == RED) {
                        node.parent.color = BLACK;
                        y.color = BLACK;
                        node.parent.parent.color = RED;
                        node = node.parent.parent;
                    } else {
                        if (node == node.parent.right) {
                            node = node.parent;
                            leftRotate(node);
                        }
                        node.parent.color = BLACK;
                        node.parent.parent.color = RED;
                        rightRotate(node.parent.parent);
                    }
                } else {
                    Node y = node.parent.parent.left;
                    if (y.color == RED) {
                        node.parent.color = BLACK;
                        y.color = BLACK;
                        node.parent.parent.color = RED;
                        node = node.parent.parent;
                    } else {
                        if (node == node.parent.left) {
                            node = node.parent;
                            rightRotate(node);
                        }
                        node.parent.color = BLACK;
                        node.parent.parent.color = RED;
                        leftRotate(node.parent.parent);
                    }
                }
            }
            root.color = BLACK;
        }
        
        void inOrder(Node node, List<String> result) {
            if (node != NIL) {
                inOrder(node.left, result);
                String color = (node.color == RED) ? "R" : "B";
                result.add(node.data + "(" + color + ")");
                inOrder(node.right, result);
            }
        }
        
        String getInOrderTraversal() {
            List<String> result = new ArrayList<>();
            inOrder(root, result);
            return String.join(" ", result);
        }
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        
        RedBlackTree rbt = new RedBlackTree();
        for (int val : arr) {
            rbt.insert(val);
        }
        
        System.out.println(rbt.getInOrderTraversal());
        
        sc.close();
    }
}
