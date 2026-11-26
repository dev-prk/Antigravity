#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int M, N;
    if (scanf("%d %d", &M, &N) != 2) {
        return 1;
    }

    if (M <= 0 || N <= 0) {
        printf("\n");
        return 0;
    }

    int **matrix = malloc(M * sizeof(int *));
    for (int i = 0; i < M; i++) {
        matrix[i] = malloc(N * sizeof(int));
    }

    int *rowSum = calloc(M, sizeof(int));
    int *colSum = calloc(N, sizeof(int));

    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            if (scanf("%d", &matrix[i][j]) != 1) {
                rowSum = realloc(rowSum, 0);
                colSum = realloc(colSum, 0);
                for (int k = 0; k < M; k++) free(matrix[k]);
                free(matrix);
                return 1;
            }
            rowSum[i] += matrix[i][j];
            colSum[j] += matrix[i][j];
        }
    }

    for (int i = 0; i < M; i++) {
        if (i > 0) printf(" ");
        printf("%d", rowSum[i]);
    }
    printf("\n");

    for (int j = 0; j < N; j++) {
        if (j > 0) printf(" ");
        printf("%d", colSum[j]);
    }
    printf("\n");

    for (int i = 0; i < M; i++) {
        free(matrix[i]);
    }
    free(matrix);
    free(rowSum);
    free(colSum);

    return 0;
}
