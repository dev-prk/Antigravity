#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct Node {
    int vertex;
    struct Node *next;
} Node;

void addEdge(Node **adj, int u, int v, int n) {
    Node *newNode = (Node *)malloc(sizeof(Node));
    newNode->vertex = v;
    newNode->next = adj[u - 1];
    adj[u - 1] = newNode;

    newNode = (Node *)malloc(sizeof(Node));
    newNode->vertex = u;
    newNode->next = adj[v - 1];
    adj[v - 1] = newNode;
}

void freeAdjacencyList(Node **adj, int n) {
    for (int i = 0; i < n; i++) {
        Node *current = adj[i];
        while (current != NULL) {
            Node *temp = current;
            current = current->next;
            free(temp);
        }
    }
    free(adj);
}

void DFS(Node **adj, int v, int *visited, int n) {
    visited[v] = 1;
    Node *current = adj[v];
    while (current != NULL) {
        if (!visited[current->vertex - 1]) {
            DFS(adj, current->vertex - 1, visited, n);
        }
        current = current->next;
    }
}

int countConnectedComponents(Node **adj, int n) {
    int *visited = (int *)calloc(n, sizeof(int));
    int count = 0;

    for (int i = 0; i < n; i++) {
        if (!visited[i]) {
            DFS(adj, i, visited, n);
            count++;
        }
    }

    free(visited);
    return count;
}

int main() {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) {
        return 1;
    }

    if (n <= 0) {
        printf("0\n");
        return 0;
    }

    Node **adj = (Node **)calloc(n, sizeof(Node *));
    if (adj == NULL) {
        return 1;
    }

    for (int i = 0; i < m; i++) {
        int u, v;
        if (scanf("%d %d", &u, &v) == 2) {
            if (u >= 1 && u <= n && v >= 1 && v <= n) {
                addEdge(adj, u, v, n);
            }
        }
    }

    int components = countConnectedComponents(adj, n);
    printf("%d\n", components);

    freeAdjacencyList(adj, n);

    return 0;
}
