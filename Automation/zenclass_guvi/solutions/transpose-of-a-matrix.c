#include <stdio.h>
#include <stdlib.h>

int main() {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    int **matrix = malloc(N * sizeof(int *));
    for (int i = 0; i < N; i++) {
        matrix[i] = malloc(N * sizeof(int));
        for (int j = 0; j < N; j++) {
            scanf("%d", &matrix[i][j]);
        }
    }
    
    for (int j = 0; j < N; j++) {
        for (int i = 0; i < N; i++) {
            printf("%d", matrix[i][j]);
            if (i < N - 1) printf(" ");
        }
        printf("\n");
    }
    
    for (int i = 0; i < N; i++) {
        free(matrix[i]);
    }
    free(matrix);
    
    return 0;
}
