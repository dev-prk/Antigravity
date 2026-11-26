import java.io.*;
import java.util.*;

public class Main {
    static int[] val;
    static List<Integer>[] adj;
    static int maxSum;
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        if (n == 0) {
            System.out.println(0);
            return;
        }
        
        val = new int[n + 1];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= n; i++) {
            val[i] = Integer.parseInt(st.nextToken());
        }
        
        adj = new ArrayList[n + 1];
        for (int i = 0; i <= n; i++) {
            adj[i] = new ArrayList<>();
        }
        
        for (int i = 0; i < n - 1; i++) {
            st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            adj[u].add(v);
            adj[v].add(u);
        }
        
        maxSum = Integer.MIN_VALUE;
        dfs(1, 0);
        System.out.println(maxSum);
    }
    
    static int dfs(int node, int parent) {
        int curVal = val[node];
        int maxChildSum = 0;
        int max1 = 0, max2 = 0;
        
        for (int child : adj[node]) {
            if (child == parent) continue;
            int childSum = dfs(child, node);
            if (childSum > 0) {
                if (childSum >= max1) {
                    max2 = max1;
                    max1 = childSum;
                } else if (childSum > max2) {
                    max2 = childSum;
                }
            }
        }
        
        int throughPath = curVal + max1 + max2;
        if (throughPath > maxSum) {
            maxSum = throughPath;
        }
        
        int returnPath = curVal + max1;
        if (returnPath > maxSum) {
            maxSum = returnPath;
        }
        
        return returnPath;
    }
}
