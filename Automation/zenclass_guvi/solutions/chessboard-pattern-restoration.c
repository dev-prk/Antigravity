#include <stdio.h>
#include <stdlib.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    int **board = (int **)malloc(n * sizeof(int *));
    for (int i = 0; i < n; i++) {
        board[i] = (int *)malloc(n * sizeof(int));
        for (int j = 0; j < n; j++) {
            scanf("%d", &board[i][j]);
        }
    }
    
    int pattern1_mismatches = 0; // Pattern starts with 0 at (0,0)
    int pattern2_mismatches = 0; // Pattern starts with 1 at (0,0)
    
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int expected1 = (i + j) % 2;
            int expected2 = 1 - expected1;
            
            if (board[i][j] != expected1) {
                pattern1_mismatches++;
            }
            if (board[i][j] != expected2) {
                pattern2_mismatches++;
            }
        }
    }
    
    int result = pattern1_mismatches;
    if (pattern2_mismatches < result) {
        result = pattern2_mismatches;
    }
    
    printf("%d\n", result);
    
    for (int i = 0; i < n; i++) {
        free(board[i]);
    }
    free(board);
    
    return 0;
}
