#include <stdio.h>
#include <stdbool.h>

#define MAX_N 1005
#define MAX_M 1005

int grid[MAX_N][MAX_M];
bool visited[MAX_N][MAX_M];
int n, m;

void floodFill(int i, int j) {
    if (i < 0 || i >= n || j < 0 || j >= m) return;
    if (visited[i][j]) return;
    if (grid[i][j] == 0) return;
    
    visited[i][j] = true;
    
    for (int dx = -1; dx <= 1; dx++) {
        for (int dy = -1; dy <= 1; dy++) {
            if (dx == 0 && dy == 0) continue;
            floodFill(i + dx, j + dy);
        }
    }
}

int countIslands() {
    int count = 0;
    
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (!visited[i][j] && grid[i][j] != 0) {
                floodFill(i, j);
                count++;
            }
        }
    }
    
    return count;
}

int main() {
    scanf("%d %d", &n, &m);
    
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            scanf("%d", &grid[i][j]);
        }
    }
    
    printf("%d\n", countIslands());
    
    return 0;
}
