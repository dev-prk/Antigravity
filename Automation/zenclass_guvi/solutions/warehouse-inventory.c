#include <stdio.h>
#include <stdlib.h>

int main() {
    int R, C, U;
    if (scanf("%d %d", &R, &C) != 2) {
        return 1;
    }
    if (scanf("%d", &U) != 1) {
        return 1;
    }

    int **grid = (int **)malloc(R * sizeof(int *));
    for (int i = 0; i < R; i++) {
        grid[i] = (int *)calloc(C, sizeof(int));
    }

    for (int u = 0; u < U; u++) {
        int r1, c1, r2, c2, value;
        if (scanf("%d %d %d %d %d", &r1, &c1, &r2, &c2, &value) != 5) {
            continue;
        }
        for (int i = r1 - 1; i < r2; i++) {
            for (int j = c1 - 1; j < c2; j++) {
                grid[i][j] += value;
            }
        }
    }

    long long total = 0;
    for (int i = 0; i < R; i++) {
        for (int j = 0; j < C; j++) {
            total += grid[i][j];
        }
    }

    printf("Total number of products: %lld\n", total);

    for (int i = 0; i < R; i++) {
        free(grid[i]);
    }
    free(grid);

    return 0;
}
