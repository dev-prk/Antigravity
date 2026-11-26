#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int M, N;
    if (scanf("%d %d", &M, &N) != 2) {
        return 0;
    }
    
    if (M <= 0 || N <= 0) {
        return 0;
    }
    
    int **mat1 = (int **)malloc(M * sizeof(int *));
    int **mat2 = (int **)malloc(M * sizeof(int *));
    int **result = (int **)malloc(M * sizeof(int *));
    
    for (int i = 0; i < M; i++) {
        mat1[i] = (int *)malloc(N * sizeof(int));
        mat2[i] = (int *)malloc(N * sizeof(int));
        result[i] = (int *)malloc(N * sizeof(int));
    }
    
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            scanf("%d", &mat1[i][j]);
        }
    }
    
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            scanf("%d", &mat2[i][j]);
        }
    }
    
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            result[i][j] = mat1[i][j] + mat2[i][j];
        }
    }
    
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            if (j > 0) {
                printf(" ");
            }
            printf("%d", result[i][j]);
        }
        printf("\n");
    }
    
    for (int i = 0; i < M; i++) {
        free(mat1[i]);
        free(mat2[i]);
        free(result[i]);
    }
    free(mat1);
    free(mat2);
    free(result);
    
    return 0;
}
