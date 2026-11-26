#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_N 1005

int adj[MAX_N][MAX_N];
int visited[MAX_N];
int parent[MAX_N];
int queue[MAX_N];
int n, m;

void bfs(int source, int dest) {
    memset(visited, 0, sizeof(visited));
    memset(parent, -1, sizeof(parent));
    
    int front = 0, rear = 0;
    queue[rear++] = source;
    visited[source] = 1;
    
    while (front < rear) {
        int u = queue[front++];
        
        if (u == dest) break;
        
        for (int v = 0; v < n; v++) {
            if (adj[u][v] && !visited[v]) {
                visited[v] = 1;
                parent[v] = u;
                queue[rear++] = v;
            }
        }
    }
}

void printPath(int source, int dest) {
    if (!visited[dest]) {
        printf("No Path");
        return;
    }
    
    int path[MAX_N];
    int count = 0;
    int current = dest;
    
    while (current != -1) {
        path[count++] = current;
        current = parent[current];
    }
    
    for (int i = count - 1; i >= 0; i--) {
        if (i < count - 1) printf(" ");
        printf("%d", path[i]);
    }
}

int main() {
    scanf("%d %d", &n, &m);
    
    memset(adj, 0, sizeof(adj));
    
    for (int i = 0; i < m; i++) {
        int u, v;
        scanf("%d %d", &u, &v);
        adj[u][v] = 1;
        adj[v][u] = 1;
    }
    
    int source, dest;
    scanf("%d %d", &source, &dest);
    
    bfs(source, dest);
    printPath(source, dest);
    printf("\n");
    
    return 0;
}
