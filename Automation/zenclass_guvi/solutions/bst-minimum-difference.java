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
    
    static class BST {
        TreeNode root;
        
        void insert(int val) {
            root = insertRec(root, val);
        }
        
        TreeNode insertRec(TreeNode node, int val) {
            if (node == null) return new TreeNode(val);
            if (val < node.val) {
                node.left = insertRec(node.left, val);
            } else {
                node.right = insertRec(node.right, val);
            }
            return node;
        }
        
        int findMinDifference() {
            List<Integer> nodes = new ArrayList<>();
            inOrderTraversal(root, nodes);
            int minDiff = Integer.MAX_VALUE;
            for (int i = 1; i < nodes.size(); i++) {
                minDiff = Math.min(minDiff, nodes.get(i) - nodes.get(i - 1));
            }
            return minDiff;
        }
        
        void inOrderTraversal(TreeNode node, List<Integer> nodes) {
            if (node == null) return;
            inOrderTraversal(node.left, nodes);
            nodes.add(node.val);
            inOrderTraversal(node.right, nodes);
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        BST bst = new BST();
        while (st.hasMoreTokens()) {
            bst.insert(Integer.parseInt(st.nextToken()));
        }
        System.out.println(bst.findMinDifference());
    }
}
