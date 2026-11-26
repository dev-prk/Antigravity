#include <stdio.h>
#include <stdbool.h>

#define MAX_N 505
#define MAX_M 505

long long grid[MAX_N][MAX_M];
bool visited[MAX_N][MAX_M];
int n, m;

int dr[] = {-1, 1, 0, 0};
int dc[] = {0, 0, -1, 1};

long long dfs(int r, int c) {
    if (r < 0 || r >= n || c < 0 || c >= m) 
        return 0;
    if (visited[r][c]) 
        return 0;
    if (grid[r][c] == 0) 
        return 0;
    
    visited[r][c] = true;
    long long sum = grid[r][c];
    
    for (int i = 0; i < 4; i++) {
        int nr = r + dr[i];
        int nc = c + dc[i];
        sum += dfs(nr, nc);
    }
    
    return sum;
}

int main() {
    scanf("%d %d", &n, &m);
    
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            scanf("%lld", &grid[i][j]);
        }
    }
    
    long long max_sum = 0;
    
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (!visited[i][j] && grid[i][j] > 0) {
                long long sum = dfs(i, j);
                if (sum > max_sum) {
                    max_sum = sum;
                }
            }
        }
    }
    
    printf("%lld\n", max_sum);
    
    return 0;
}
