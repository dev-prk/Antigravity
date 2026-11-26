#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    int R, C;
    if (scanf("%d %d", &R, &C) != 2) {
        return 1;
    }

    if (R <= 0 || C <= 0) {
        printf("Row Sums:\nColumn Sums:\n");
        return 0;
    }

    int **matrix = (int **)calloc(R, sizeof(int *));
    if (!matrix) {
        return 1;
    }

    for (int i = 0; i < R; i++) {
        matrix[i] = (int *)calloc(C, sizeof(int));
        if (!matrix[i]) {
            for (int j = 0; j < i; j++) {
                free(matrix[j]);
            }
            free(matrix);
            return 1;
        }
    }

    for (int i = 0; i < R; i++) {
        for (int j = 0; j < C; j++) {
            if (scanf("%d", &matrix[i][j]) != 1) {
                for (int k = 0; k <= i; k++) {
                    free(matrix[k]);
                }
                free(matrix);
                return 1;
            }
        }
    }

    int *colSums = (int *)calloc(C, sizeof(int));
    if (!colSums) {
        for (int i = 0; i < R; i++) {
            free(matrix[i]);
        }
        free(matrix);
        return 1;
    }

    printf("Row Sums:\n");
    for (int i = 0; i < R; i++) {
        int rowSum = 0;
        for (int j = 0; j < C; j++) {
            rowSum += matrix[i][j];
            colSums[j] += matrix[i][j];
        }
        printf("%d\n", rowSum);
    }

    printf("Column Sums:\n");
    for (int j = 0; j < C; j++) {
        if (j > 0) {
            printf(" ");
        }
        printf("%d", colSums[j]);
    }
    printf("\n");

    free(colSums);
    for (int i = 0; i < R; i++) {
        free(matrix[i]);
    }
    free(matrix);

    return 0;
}
