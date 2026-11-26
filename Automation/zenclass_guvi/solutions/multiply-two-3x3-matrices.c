#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int a[3][3], b[3][3], res[3][3];
    
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            scanf("%d", &a[i][j]);
        }
    }
    
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            scanf("%d", &b[i][j]);
        }
    }
    
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            res[i][j] = 0;
            for (int k = 0; k < 3; k++) {
                res[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            printf("%d", res[i][j]);
            if (j < 2) {
                printf(" ");
            }
        }
        printf("\n");
    }
    
    return 0;
}
