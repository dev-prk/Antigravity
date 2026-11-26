import java.io.*;
import java.util.*;

public class Main {

    static class Node {
        int key, height;
        Node left, right;
        Node(int k) { key = k; height = 1; }
    }

    static int h(Node n) { return n == null ? 0 : n.height; }

    static void update(Node n) {
        if (n != null) {
            n.height = 1 + Math.max(h(n.left), h(n.right));
        }
    }

    static int bal(Node n) { return n == null ? 0 : h(n.left) - h(n.right); }

    static Node rotateRight(Node y) {
        Node x = y.left;
        Node t = x.right;
        x.right = y;
        y.left = t;
        update(y);
        update(x);
        return x;
    }

    static Node rotateLeft(Node x) {
        Node y = x.right;
        Node t = y.left;
        y.left = x;
        x.right = t;
        update(x);
        update(y);
        return y;
    }

    static Node balance(Node n) {
        if (n == null) return null;
        update(n);
        int b = bal(n);
        if (b > 1) {
            if (bal(n.left) < 0) {
                n.left = rotateLeft(n.left);
            }
            return rotateRight(n);
        }
        if (b < -1) {
            if (bal(n.right) > 0) {
                n.right = rotateRight(n.right);
            }
            return rotateLeft(n);
        }
        return n;
    }

    static Node insert(Node root, int key) {
        if (root == null) return new Node(key);
        if (key < root.key) {
            root.left = insert(root.left, key);
        } else if (key > root.key) {
            root.right = insert(root.right, key);
        } else {
            return root;
        }
        return balance(root);
    }

    static Node minValueNode(Node node) {
        Node current = node;
        while (current.left != null) {
            current = current.left;
        }
        return current;
    }

    static Node delete(Node root, int key) {
        if (root == null) return null;
        if (key < root.key) {
            root.left = delete(root.left, key);
        } else if (key > root.key) {
            root.right = delete(root.right, key);
        } else {
            if (root.left == null) {
                return root.right;
            } else if (root.right == null) {
                return root.left;
            }
            Node temp = minValueNode(root.right);
            root.key = temp.key;
            root.right = delete(root.right, temp.key);
        }
        return balance(root);
    }

    static void inorder(Node root, StringBuilder sb) {
        if (root == null) return;
        inorder(root.left, sb);
        if (sb.length() > 0) sb.append(' ');
        sb.append(root.key);
        inorder(root.right, sb);
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        Node root = null;
        for (int i = 0; i < N; i++) {
            int val = Integer.parseInt(st.nextToken());
            root = insert(root, val);
        }
        int K = Integer.parseInt(br.readLine().trim());
        root = delete(root, K);
        StringBuilder sb = new StringBuilder();
        inorder(root, sb);
        System.out.println(sb.toString());
    }
}
