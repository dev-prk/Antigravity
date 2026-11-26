import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(parts[0]);
        int m = Integer.parseInt(parts[1]);
        
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i <= n; i++) {
            adj.add(new ArrayList<>());
        }
        
        for (int i = 0; i < m; i++) {
            parts = br.readLine().trim().split("\\s+");
            int u = Integer.parseInt(parts[0]);
            int v = Integer.parseInt(parts[1]);
            adj.get(u).add(v);
        }
        
        int[] state = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            if (state[i] == 0) {
                if (hasCycle(adj, state, i)) {
                    System.out.println("Yes");
                    return;
                }
            }
        }
        System.out.println("No");
    }
    
    static boolean hasCycle(List<List<Integer>> adj, int[] state, int node) {
        state[node] = 1;
        for (int neighbor : adj.get(node)) {
            if (state[neighbor] == 1) {
                return true;
            }
            if (state[neighbor] == 0) {
                if (hasCycle(adj, state, neighbor)) {
                    return true;
                }
            }
        }
        state[node] = 2;
        return false;
    }
}
