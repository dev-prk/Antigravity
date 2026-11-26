#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

void getInputMatrix(int matrix[][100], int n, int m) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            scanf("%d", &matrix[i][j]);
        }
    }
}

int findMaxPathSum(int matrix[][100], int n, int m) {
    if (n == 0 || m == 0) {
        return 0;
    }
    
    int dp[100][100];
    dp[0][0] = matrix[0][0];
    
    for (int j = 1; j < m; j++) {
        dp[0][j] = dp[0][j-1] + matrix[0][j];
    }
    
    for (int i = 1; i < n; i++) {
        dp[i][0] = dp[i-1][0] + matrix[i][0];
    }
    
    for (int i = 1; i < n; i++) {
        for (int j = 1; j < m; j++) {
            if (dp[i-1][j] > dp[i][j-1]) {
                dp[i][j] = dp[i-1][j] + matrix[i][j];
            } else {
                dp[i][j] = dp[i][j-1] + matrix[i][j];
            }
        }
    }
    
    return dp[n-1][m-1];
}

int main() {
    int n, m;
    scanf("%d %d", &n, &m);
    
    int matrix[100][100];
    getInputMatrix(matrix, n, m);
    
    int result = findMaxPathSum(matrix, n, m);
    printf("%d\n", result);
    
    return 0;
}
