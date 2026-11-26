#include <stdio.h>
#include <stdlib.h>

void add_arrays(int n, int * restrict a, int * restrict b, int * restrict result) {
    for (int i = 0; i < n; i++) {
        result[i] = a[i] + b[i];
    }
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    
    if (n < 1 || n > 1000) {
        return 1;
    }
    
    int *a = malloc(n * sizeof(int));
    int *b = malloc(n * sizeof(int));
    int *result = malloc(n * sizeof(int));
    
    if (!a || !b || !result) {
        free(a);
        free(b);
        free(result);
        return 1;
    }
    
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &a[i]) != 1) {
            free(a);
            free(b);
            free(result);
            return 1;
        }
    }
    
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &b[i]) != 1) {
            free(a);
            free(b);
            free(result);
            return 1;
        }
    }
    
    add_arrays(n, a, b, result);
    
    for (int i = 0; i < n; i++) {
        if (i > 0) {
            printf(" ");
        }
        printf("%d", result[i]);
    }
    printf("\n");
    
    free(a);
    free(b);
    free(result);
    
    return 0;
}
