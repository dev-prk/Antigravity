import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

public class Main {
    static class Node {
        int data;
        Node left, right;
        Node(int data) {
            this.data = data;
            left = right = null;
        }
    }

    public static Node insert(Node root, int data) {
        if (root == null) {
            return new Node(data);
        }
        if (data < root.data) {
            root.left = insert(root.left, data);
        } else {
            root.right = insert(root.right, data);
        }
        return root;
    }

    public static int findMin(Node root) {
        Node current = root;
        while (current.left != null) {
            current = current.left;
        }
        return current.data;
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        if (n <= 0) {
            System.out.println(-1);
            return;
        }
        
        StringTokenizer st = new StringTokenizer(br.readLine());
        Node root = null;
        
        if (st.countTokens() > 0) {
            int first = Integer.parseInt(st.nextToken());
            root = new Node(first);
        }
        
        while (st.hasMoreTokens()) {
            int data = Integer.parseInt(st.nextToken());
            root = insert(root, data);
        }
        
        System.out.println(findMin(root));
    }
}
