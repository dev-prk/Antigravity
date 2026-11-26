import java.io.*;
import java.util.*;

public class Main {
    static int time;
    static List<List<Integer>> adj;
    static List<int[]> bridges;
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(parts[0]);
        int m = Integer.parseInt(parts[1]);
        
        adj = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            adj.add(new ArrayList<>());
        }
        
        for (int i = 0; i < m; i++) {
            parts = br.readLine().trim().split("\\s+");
            int u = Integer.parseInt(parts[0]);
            int v = Integer.parseInt(parts[1]);
            adj.get(u).add(v);
            adj.get(v).add(u);
        }
        
        time = 0;
        bridges = new ArrayList<>();
        int[] disc = new int[n];
        int[] low = new int[n];
        boolean[] visited = new boolean[n];
        Arrays.fill(disc, -1);
        
        for (int i = 0; i < n; i++) {
            if (!visited[i]) {
                dfs(i, -1, disc, low, visited);
            }
        }
        
        for (int[] bridge : bridges) {
            System.out.println(bridge[0] + " " + bridge[1]);
        }
    }
    
    static void dfs(int u, int parent, int[] disc, int[] low, boolean[] visited) {
        visited[u] = true;
        disc[u] = low[u] = time++;
        
        for (int v : adj.get(u)) {
            if (!visited[v]) {
                dfs(v, u, disc, low, visited);
                low[u] = Math.min(low[u], low[v]);
                
                if (low[v] > disc[u]) {
                    bridges.add(new int[]{Math.min(u, v), Math.max(u, v)});
                }
            } else if (v != parent) {
                low[u] = Math.min(low[u], disc[v]);
            }
        }
    }
}
