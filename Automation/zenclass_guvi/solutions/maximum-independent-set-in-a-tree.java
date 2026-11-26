import java.io.*;
import java.util.*;

public class Main {
    static List<Integer>[] adj;
    static int[] include, exclude;
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        if (n == 0) {
            System.out.println(0);
            return;
        }
        
        adj = new ArrayList[n + 1];
        for (int i = 1; i <= n; i++) {
            adj[i] = new ArrayList<>();
        }
        
        for (int i = 0; i < n - 1; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            adj[u].add(v);
            adj[v].add(u);
        }
        
        include = new int[n + 1];
        exclude = new int[n + 1];
        
        dfs(1, 0);
        
        System.out.println(Math.max(include[1], exclude[1]));
    }
    
    static void dfs(int node, int parent) {
        include[node] = 1;
        exclude[node] = 0;
        
        for (int child : adj[node]) {
            if (child != parent) {
                dfs(child, node);
                include[node] += exclude[child];
                exclude[node] += Math.max(include[child], exclude[child]);
            }
        }
    }
}
