#include <stdio.h>
int main(void) {
    int m, n;
    scanf("%d %d", &m, &n);
    int matrix[100][100];
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            scanf("%d", &matrix[i][j]);
        }
    }
    for (int j = 0; j < n; j++) {
        for (int i = 0; i < m; i++) {
            printf("%d", matrix[i][j]);
            if (i < m - 1) {
                printf(" ");
            }
        }
        printf("\n");
    }
    return 0;
}
