import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] values = new int[N];
        for (int i = 0; i < N; i++) {
            values[i] = Integer.parseInt(st.nextToken());
        }

        int rootValue = values[0];

        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i <= 100000; i++) {
            adj.add(new ArrayList<>());
        }

        for (int i = 0; i < N - 1; i++) {
            st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            adj.get(u).add(v);
            adj.get(v).add(u);
        }

        Map<Integer, List<Integer>> children = new HashMap<>();
        for (int val : values) {
            children.put(val, new ArrayList<>());
        }

        Queue<Integer> q = new LinkedList<>();
        q.add(rootValue);
        Set<Integer> visited = new HashSet<>();
        visited.add(rootValue);

        while (!q.isEmpty()) {
            int current = q.poll();
            for (int neighbor : adj.get(current)) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor);
                    children.get(current).add(neighbor);
                    q.add(neighbor);
                }
            }
        }

        List<Integer> path = new ArrayList<>();
        dfs(rootValue, children, path);
    }

    private static void dfs(int node, Map<Integer, List<Integer>> children, List<Integer> path) {
        path.add(node);
        List<Integer> nodeChildren = children.get(node);
        if (nodeChildren.isEmpty()) {
            for (int i = 0; i < path.size(); i++) {
                if (i > 0) System.out.print(" ");
                System.out.print(path.get(i));
            }
            System.out.println();
        } else {
            for (int child : nodeChildren) {
                dfs(child, children, path);
            }
        }
        path.remove(path.size() - 1);
    }
}
