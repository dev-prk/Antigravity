import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int data;
        Node left, right;
        Node(int d) { data = d; }
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nStr = br.readLine();
        if (nStr == null || nStr.trim().isEmpty()) {
            System.out.println();
            return;
        }
        int n = Integer.parseInt(nStr.trim());
        if (n <= 0) {
            System.out.println();
            return;
        }
        String line = br.readLine();
        if (line == null) line = "";
        String[] parts = line.trim().split("\\s+");
        int[] vals = new int[n];
        for (int i = 0; i < n && i < parts.length; i++) {
            vals[i] = Integer.parseInt(parts[i]);
        }
        Node root = buildTree(vals);
        List<Integer> result = levelOrder(root);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < result.size(); i++) {
            if (i > 0) sb.append(' ');
            sb.append(result.get(i));
        }
        sb.append(' ');
        System.out.println(sb.toString());
    }

    static Node buildTree(int[] vals) {
        if (vals.length == 0 || vals[0] == -1) return null;
        Node root = new Node(vals[0]);
        Queue<Node> q = new LinkedList<>();
        q.offer(root);
        int idx = 1;
        while (idx < vals.length) {
            Node curr = q.poll();
            if (curr == null) continue;
            if (idx < vals.length && vals[idx] != -1) {
                curr.left = new Node(vals[idx]);
                q.offer(curr.left);
            }
            idx++;
            if (idx < vals.length && vals[idx] != -1) {
                curr.right = new Node(vals[idx]);
                q.offer(curr.right);
            }
            idx++;
        }
        return root;
    }

    static List<Integer> levelOrder(Node root) {
        List<Integer> result = new ArrayList<>();
        if (root == null) return result;
        Queue<Node> q = new LinkedList<>();
        q.offer(root);
        while (!q.isEmpty()) {
            Node curr = q.poll();
            result.add(curr.data);
            if (curr.left != null) q.offer(curr.left);
            if (curr.right != null) q.offer(curr.right);
        }
        return result;
    }
}
