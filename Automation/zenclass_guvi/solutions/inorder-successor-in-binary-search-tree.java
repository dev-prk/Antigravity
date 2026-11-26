import java.io.*;
import java.util.*;

public class Main {
    static class TreeNode {
        int val;
        TreeNode left, right;
        TreeNode(int val) {
            this.val = val;
        }
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s;
        
        while ((s = br.readLine()) != null && s.trim().isEmpty()) {}
        if (s == null) return;
        
        int N = Integer.parseInt(s.trim());
        
        if (N == 0) {
            br.readLine();
            System.out.println("null");
            return;
        }

        String[] parts = br.readLine().trim().split("\\s+");
        int[] values = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            values[i] = Integer.parseInt(parts[i]);
        }

        String kLine = br.readLine();
        while (kLine != null && kLine.trim().isEmpty()) {
            kLine = br.readLine();
        }
        int K = Integer.parseInt(kLine.trim());

        TreeNode root = null;
        boolean foundTarget = false;
        for (int v : values) {
            if (v == K) foundTarget = true;
            root = insert(root, v);
        }

        if (!foundTarget) {
            System.out.println("null");
            return;
        }

        TreeNode successor = inorderSuccessor(root, K);
        if (successor == null) {
            System.out.println("null");
        } else {
            System.out.println(successor.val);
        }
    }

    static TreeNode insert(TreeNode root, int val) {
        if (root == null) return new TreeNode(val);
        if (val < root.val) {
            root.left = insert(root.left, val);
        } else {
            root.right = insert(root.right, val);
        }
        return root;
    }

    static TreeNode inorderSuccessor(TreeNode root, int K) {
        TreeNode successor = null;
        while (root != null) {
            if (K < root.val) {
                successor = root;
                root = root.left;
            } else if (K > root.val) {
                root = root.right;
            } else {
                if (root.right != null) {
                    successor = root.right;
                    while (successor.left != null) {
                        successor = successor.left;
                    }
                }
                break;
            }
        }
        return successor;
    }
}
