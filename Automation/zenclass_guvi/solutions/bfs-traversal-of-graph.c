#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_N 100005

int visited[MAX_N];
int adj_head[MAX_N];
int adj_list[2 * MAX_N];
int adj_next[2 * MAX_N];
int adj_cnt = 0;

int queue[MAX_N];
int front, rear;

void bfs(int s, int n) {
    memset(visited, 0, sizeof(visited));
    front = rear = 0;
    
    queue[rear++] = s;
    visited[s] = 1;
    
    int first = 1;
    
    while (front < rear) {
        int u = queue[front++];
        
        if (!first) printf(" ");
        first = 0;
        printf("%d", u);
        
        for (int i = adj_head[u]; i != -1; i = adj_next[i]) {
            int v = adj_list[i];
            if (!visited[v]) {
                visited[v] = 1;
                queue[rear++] = v;
            }
        }
    }
    printf("\n");
}

int main() {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) {
        return 0;
    }
    
    memset(adj_head, -1, sizeof(adj_head));
    adj_cnt = 0;
    
    for (int i = 0; i < m; i++) {
        int u, v;
        if (scanf("%d %d", &u, &v) == 2) {
            adj_list[adj_cnt] = v;
            adj_next[adj_cnt] = adj_head[u];
            adj_head[u] = adj_cnt++;
            
            adj_list[adj_cnt] = u;
            adj_next[adj_cnt] = adj_head[v];
            adj_head[v] = adj_cnt++;
        }
    }
    
    int s;
    if (scanf("%d", &s) == 1) {
        bfs(s, n);
    }
    
    return 0;
}
