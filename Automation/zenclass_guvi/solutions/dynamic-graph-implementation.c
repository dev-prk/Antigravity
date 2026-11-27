#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_VERTICES 1000

typedef struct AdjNode {
    int vertex;
    struct AdjNode* next;
} AdjNode;

typedef struct Graph {
    int numVertices;
    AdjNode* adjList[MAX_VERTICES];
} Graph;

Graph* createGraph() {
    Graph* graph = (Graph*)malloc(sizeof(Graph));
    graph->numVertices = 0;
    for (int i = 0; i < MAX_VERTICES; i++) {
        graph->adjList[i] = NULL;
    }
    return graph;
}

void addVertex(Graph* graph, int vertex) {
    if (vertex >= graph->numVertices) {
        graph->numVertices = vertex + 1;
    }
}

void addEdge(Graph* graph, int src, int dest) {
    AdjNode* newNode = (AdjNode*)malloc(sizeof(AdjNode));
    newNode->vertex = dest;
    newNode->next = graph->adjList[src];
    graph->adjList[src] = newNode;
}

void printAdjList(Graph* graph) {
    for (int i = 0; i < graph->numVertices; i++) {
        if (graph->adjList[i] != NULL) {
            printf("%d: [", i);
            AdjNode* current = graph->adjList[i];
            while (current != NULL) {
                printf("%d", current->vertex);
                if (current->next != NULL) {
                    printf(", ");
                }
                current = current->next;
            }
            printf("]\n");
        }
    }
}

int main() {
    int n;
    scanf("%d", &n);
    
    Graph* graph = createGraph();
    
    char operation[20];
    for (int i = 0; i < n; i++) {
        scanf("%s", operation);
        
        if (strcmp(operation, "ADD_VERTEX") == 0) {
            int vertex;
            scanf("%d", &vertex);
            addVertex(graph, vertex);
        } else if (strcmp(operation, "ADD_EDGE") == 0) {
            int src, dest;
            scanf("%d", &src);
            scanf("%d", &dest);
            addEdge(graph, src, dest);
        } else if (strcmp(operation, "PRINT_ADJ_LIST") == 0) {
            printAdjList(graph);
        }
    }
    
    return 0;
}
