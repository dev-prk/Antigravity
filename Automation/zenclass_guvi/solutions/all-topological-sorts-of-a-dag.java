import java.io.*;
import java.util.*;

public class Main {
    static int n, m;
    static List<Integer>[] adj;
    static int[] inDegree;
    static StringBuilder sb = new StringBuilder();
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        n = Integer.parseInt(st.nextToken());
        m = Integer.parseInt(st.nextToken());
        
        adj = new ArrayList[n + 1];
        inDegree = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            adj[i] = new ArrayList<>();
        }
        
        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            adj[u].add(v);
            inDegree[v]++;
        }
        
        List<Integer> current = new ArrayList<>();
        generateTopologicalSorts(current, 0);
        System.out.print(sb.toString());
    }
    
    static void generateTopologicalSorts(List<Integer> current, int pos) {
        if (pos == n) {
            for (int i = 0; i < n; i++) {
                if (i > 0) sb.append(' ');
                sb.append(current.get(i));
            }
            sb.append('\n');
            return;
        }
        
        List<Integer> candidates = new ArrayList<>();
        for (int i = 1; i <= n; i++) {
            if (inDegree[i] == 0 && !current.contains(i)) {
                candidates.add(i);
            }
        }
        
        Collections.sort(candidates);
        
        for (int u : candidates) {
            current.add(u);
            for (int v : adj[u]) {
                inDegree[v]--;
            }
            
            generateTopologicalSorts(current, pos + 1);
            
            current.remove(current.size() - 1);
            for (int v : adj[u]) {
                inDegree[v]++;
            }
        }
    }
}
