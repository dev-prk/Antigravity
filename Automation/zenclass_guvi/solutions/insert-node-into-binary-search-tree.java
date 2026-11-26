import java.util.*;
import java.io.*;

public class Main {
    static class TreeNode {
        int val;
        TreeNode left, right;
        TreeNode(int v) { val = v; }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        // Read first line (BST level order)
        String line1 = sc.nextLine().trim();
        int insertVal = sc.nextInt();
        
        // Handle empty input
        if (line1.isEmpty()) {
            TreeNode root = new TreeNode(insertVal);
            System.out.println("" + insertVal);
            return;
        }
        
        // Parse initial BST
        String[] parts = line1.split("\\s+");
        TreeNode root = buildTree(parts);
        
        // Insert node
        root = insertNode(root, insertVal);
        
        // Output level order
        System.out.println(levelOrder(root));
    }

    static TreeNode buildTree(String[] parts) {
        if (parts.length == 0 || "null".equals(parts[0])) return null;
        
        TreeNode root = new TreeNode(Integer.parseInt(parts[0]));
        Queue<TreeNode> q = new LinkedList<>();
        q.offer(root);
        
        int i = 1;
        while (!q.isEmpty() && i < parts.length) {
            TreeNode node = q.poll();
            
            // Left child
            if (i < parts.length) {
                if (!"null".equals(parts[i])) {
                    node.left = new TreeNode(Integer.parseInt(parts[i]));
                    q.offer(node.left);
                }
                i++;
            }
            
            // Right child
            if (i < parts.length) {
                if (!"null".equals(parts[i])) {
                    node.right = new TreeNode(Integer.parseInt(parts[i]));
                    q.offer(node.right);
                }
                i++;
            }
        }
        
        return root;
    }

    static TreeNode insertNode(TreeNode root, int val) {
        if (root == null) return new TreeNode(val);
        
        if (val < root.val) {
            root.left = insertNode(root.left, val);
        } else {
            root.right = insertNode(root.right, val);
        }
        
        return root;
    }

    static String levelOrder(TreeNode root) {
        if (root == null) return "null";
        
        StringBuilder sb = new StringBuilder();
        Queue<TreeNode> q = new LinkedList<>();
        q.offer(root);
        
        while (!q.isEmpty()) {
            TreeNode node = q.poll();
            
            if (node == null) {
                sb.append("null ");
                continue;
            }
            
            sb.append(node.val).append(" ");
            q.offer(node.left);
            q.offer(node.right);
        }
        
        // Remove trailing nulls and space
        String result = sb.toString().trim();
        // Remove trailing "null" if any
        int lastNonNull = result.lastIndexOf("1");
        if (lastNonNull == -1) lastNonNull = result.lastIndexOf("2");
        if (lastNonNull == -1) lastNonNull = result.lastIndexOf("3");
        if (lastNonNull == -1) lastNonNull = result.lastIndexOf("4");
        if (lastNonNull == -1) lastNonNull = result.lastIndexOf("5");
        if (lastNonNull == -1) lastNonNull = result.lastIndexOf("6");
        if (lastNonNull == -1) lastNonNull = result.lastIndexOf("7");
        if (lastNonNull == -1) lastNonNull = result.lastIndexOf("8");
        if (lastNonNull == -1) lastNonNull = result.lastIndexOf("9");
        if (lastNonNull == -1) lastNonNull = result.lastIndexOf("0");
        
        // Actually, just truncate at the last space
        // Check if ends with " null" and remove trailing nulls
        while (result.endsWith(" null")) {
            result = result.substring(0, result.length() - 5);
        }
        
        return result;
    }
}
