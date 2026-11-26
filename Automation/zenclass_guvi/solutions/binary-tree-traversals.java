import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int val;
        Node left, right;
        Node(int val) { this.val = val; }
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        if (line == null || line.isEmpty()) return;
        int n = Integer.parseInt(line.trim());
        
        Map<Integer, Node> nodeMap = new HashMap<>();
        Map<Integer, Integer> childCount = new HashMap<>();
        Node root = null;
        
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int nodeVal = Integer.parseInt(st.nextToken());
            int leftVal = Integer.parseInt(st.nextToken());
            int rightVal = Integer.parseInt(st.nextToken());
            
            Node node = nodeMap.computeIfAbsent(nodeVal, Node::new);
            childCount.put(nodeVal, 0);
            
            if (leftVal != -1) {
                Node leftNode = nodeMap.computeIfAbsent(leftVal, Node::new);
                node.left = leftNode;
                childCount.put(leftVal, childCount.getOrDefault(leftVal, 0));
            }
            if (rightVal != -1) {
                Node rightNode = nodeMap.computeIfAbsent(rightVal, Node::new);
                node.right = rightNode;
                childCount.put(rightVal, childCount.getOrDefault(rightVal, 0));
            }
        }
        
        Set<Integer> children = new HashSet<>();
        for (Map.Entry<Integer, Node> entry : nodeMap.entrySet()) {
            Node node = entry.getValue();
            if (node.left != null) children.add(node.left.val);
            if (node.right != null) children.add(node.right.val);
        }
        
        for (Integer val : nodeMap.keySet()) {
            if (!children.contains(val)) {
                root = nodeMap.get(val);
                break;
            }
        }
        
        List<Integer> inorder = new ArrayList<>();
        List<Integer> preorder = new ArrayList<>();
        List<Integer> postorder = new ArrayList<>();
        
        inorder(root, inorder);
        preorder(root, preorder);
        postorder(root, postorder);
        
        System.out.println(intListToStr(inorder));
        System.out.println(intListToStr(preorder));
        System.out.println(intListToStr(postorder));
    }
    
    static void inorder(Node node, List<Integer> result) {
        if (node == null) return;
        inorder(node.left, result);
        result.add(node.val);
        inorder(node.right, result);
    }
    
    static void preorder(Node node, List<Integer> result) {
        if (node == null) return;
        result.add(node.val);
        preorder(node.left, result);
        preorder(node.right, result);
    }
    
    static void postorder(Node node, List<Integer> result) {
        if (node == null) return;
        postorder(node.left, result);
        postorder(node.right, result);
        result.add(node.val);
    }
    
    static String intListToStr(List<Integer> list) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < list.size(); i++) {
            if (i > 0) sb.append(' ');
            sb.append(list.get(i));
        }
        return sb.toString();
    }
}
