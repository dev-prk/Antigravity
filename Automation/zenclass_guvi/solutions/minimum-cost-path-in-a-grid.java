import java.io.*;
import java.util.*;

public class Main {
    static class State {
        int cost, row, col;
        State(int cost, int row, int col) {
            this.cost = cost;
            this.row = row;
            this.col = col;
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int m = Integer.parseInt(parts[0]);
        int n = Integer.parseInt(parts[1]);

        if (m <= 0 || n <= 0) {
            System.out.println(0);
            return;
        }

        int[][] grid = new int[m][n];
        for (int i = 0; i < m; i++) {
            parts = br.readLine().trim().split("\\s+");
            for (int j = 0; j < n; j++) {
                grid[i][j] = Integer.parseInt(parts[j]);
            }
        }

        if (m == 1 && n == 1) {
            System.out.println(grid[0][0]);
            return;
        }

        int[][] dist = new int[m][n];
        for (int[] row : dist) Arrays.fill(row, Integer.MAX_VALUE);
        dist[0][0] = grid[0][0];

        boolean[][] visited = new boolean[m][n];
        PriorityQueue<State> pq = new PriorityQueue<>(Comparator.comparingInt(s -> s.cost));
        pq.offer(new State(grid[0][0], 0, 0));

        int[] dr = {1, 0};
        int[] dc = {0, 1};

        while (!pq.isEmpty()) {
            State curr = pq.poll();
            int r = curr.row, c = curr.col;

            if (visited[r][c]) continue;
            visited[r][c] = true;

            if (r == m - 1 && c == n - 1) {
                System.out.println(dist[r][c]);
                return;
            }

            for (int k = 0; k < 2; k++) {
                int nr = r + dr[k], nc = c + dc[k];
                if (nr < m && nc < n && !visited[nr][nc]) {
                    int newCost = dist[r][c] + grid[nr][nc];
                    if (newCost < dist[nr][nc]) {
                        dist[nr][nc] = newCost;
                        pq.offer(new State(newCost, nr, nc));
                    }
                }
            }
        }

        System.out.println(dist[m-1][n-1]);
    }
}
