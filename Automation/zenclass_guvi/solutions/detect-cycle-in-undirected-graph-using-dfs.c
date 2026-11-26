#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_N 1005

int visited[MAX_N];
int parent[MAX_N];
int adj[MAX_N][MAX_N];
int adj_size[MAX_N];
int has_cycle;

void dfs(int u, int p) {
    visited[u] = 1;
    parent[u] = p;
    
    for (int i = 0; i < adj_size[u]; i++) {
        int v = adj[u][i];
        if (!visited[v]) {
            dfs(v, u);
            if (has_cycle) return;
        } else if (v != p) {
            has_cycle = 1;
            return;
        }
    }
}

int main() {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) {
        printf("No Cycle\n");
        return 0;
    }
    
    if (n == 0 || m == 0) {
        printf("No Cycle\n");
        return 0;
    }
    
    memset(visited, 0, sizeof(visited));
    memset(parent, -1, sizeof(parent));
    memset(adj_size, 0, sizeof(adj_size));
    has_cycle = 0;
    
    for (int i = 0; i < m; i++) {
        int u, v;
        if (scanf("%d %d", &u, &v) == 2) {
            if (u >= 0 && u < n && v >= 0 && v < n) {
                adj[u][adj_size[u]] = v;
                adj_size[u]++;
                adj[v][adj_size[v]] = u;
                adj_size[v]++;
            }
        }
    }
    
    for (int i = 0; i < n && !has_cycle; i++) {
        if (!visited[i]) {
            dfs(i, -1);
        }
    }
    
    if (has_cycle) {
        printf("Cycle Found\n");
    } else {
        printf("No Cycle\n");
    }
    
    return 0;
}
