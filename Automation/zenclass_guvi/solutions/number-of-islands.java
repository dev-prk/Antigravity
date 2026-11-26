import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().trim().split("\\s+");
        int m = Integer.parseInt(parts[0]);
        int n = Integer.parseInt(parts[1]);
        
        if (m <= 0 || n <= 0) {
            System.out.println(0);
            return;
        }
        
        char[][] grid = new char[m][n];
        for (int i = 0; i < m; i++) {
            String line = br.readLine();
            if (line != null && line.length() >= n) {
                grid[i] = line.substring(0, n).toCharArray();
            } else {
                grid[i] = new char[n];
            }
        }
        
        System.out.println(countIslands(grid));
    }
    
    private static int countIslands(char[][] grid) {
        int m = grid.length;
        int n = grid[0].length;
        boolean[][] visited = new boolean[m][n];
        int count = 0;
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == '1' && !visited[i][j]) {
                    dfs(grid, visited, i, j, m, n);
                    count++;
                }
            }
        }
        
        return count;
    }
    
    private static void dfs(char[][] grid, boolean[][] visited, int i, int j, int m, int n) {
        if (i < 0 || i >= m || j < 0 || j >= n || grid[i][j] == '0' || visited[i][j]) {
            return;
        }
        
        visited[i][j] = true;
        dfs(grid, visited, i + 1, j, m, n);
        dfs(grid, visited, i - 1, j, m, n);
        dfs(grid, visited, i, j + 1, m, n);
        dfs(grid, visited, i, j - 1, m, n);
    }
}
