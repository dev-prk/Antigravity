#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int M, N;
    if (scanf("%d %d", &M, &N) != 2) {
        return 1;
    }
    
    if (M <= 0 || N <= 0 || M > 100 || N > 100) {
        printf("-1\n");
        return 0;
    }
    
    int **grid = (int **)malloc(M * sizeof(int *));
    for (int i = 0; i < M; i++) {
        grid[i] = (int *)malloc(N * sizeof(int));
    }
    
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            if (scanf("%d", &grid[i][j]) != 1) {
                for (int k = 0; k <= i; k++) {
                    free(grid[k]);
                }
                free(grid);
                printf("-1\n");
                return 1;
            }
            if (grid[i][j] < 1 || grid[i][j] > 100) {
                for (int k = 0; k <= i; k++) {
                    free(grid[k]);
                }
                free(grid);
                printf("-1\n");
                return 1;
            }
        }
    }
    
    int **dp = (int **)malloc(M * sizeof(int *));
    for (int i = 0; i < M; i++) {
        dp[i] = (int *)malloc(N * sizeof(int));
    }
    
    dp[0][0] = grid[0][0];
    
    for (int j = 1; j < N; j++) {
        dp[0][j] = dp[0][j-1] + grid[0][j];
    }
    
    for (int i = 1; i < M; i++) {
        dp[i][0] = dp[i-1][0] + grid[i][0];
    }
    
    for (int i = 1; i < M; i++) {
        for (int j = 1; j < N; j++) {
            if (dp[i-1][j] < dp[i][j-1]) {
                dp[i][j] = dp[i-1][j] + grid[i][j];
            } else {
                dp[i][j] = dp[i][j-1] + grid[i][j];
            }
        }
    }
    
    printf("%d\n", dp[M-1][N-1]);
    
    for (int i = 0; i < M; i++) {
        free(dp[i]);
    }
    free(dp);
    
    for (int i = 0; i < M; i++) {
        free(grid[i]);
    }
    free(grid);
    
    return 0;
}
