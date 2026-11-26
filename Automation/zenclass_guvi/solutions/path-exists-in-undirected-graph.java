import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] nm = br.readLine().trim().split("\\s+");
        int n = Integer.parseInt(nm[0]);
        int m = Integer.parseInt(nm[1]);
        
        List<Integer>[] adj = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            adj[i] = new ArrayList<>();
        }
        
        for (int i = 0; i < m; i++) {
            String[] uv = br.readLine().trim().split("\\s+");
            int u = Integer.parseInt(uv[0]);
            int v = Integer.parseInt(uv[1]);
            adj[u].add(v);
            adj[v].add(u);
        }
        
        String[] startEnd = br.readLine().trim().split("\\s+");
        int start = Integer.parseInt(startEnd[0]);
        int end = Integer.parseInt(startEnd[1]);
        
        if (start == end) {
            System.out.println("Yes");
            return;
        }
        
        boolean[] visited = new boolean[n];
        Deque<Integer> queue = new ArrayDeque<>();
        queue.offer(start);
        visited[start] = true;
        
        while (!queue.isEmpty()) {
            int curr = queue.poll();
            for (int next : adj[curr]) {
                if (next == end) {
                    System.out.println("Yes");
                    return;
                }
                if (!visited[next]) {
                    visited[next] = true;
                    queue.offer(next);
                }
            }
        }
        
        System.out.println("No");
    }
}
