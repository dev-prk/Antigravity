#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int n, k;
    
    if (scanf("%d", &n) != 1) {
        return 0;
    }
    
    int *arr = NULL;
    if (n > 0) {
        arr = (int *)malloc((size_t)n * sizeof(int));
        if (arr == NULL) {
            return 1;
        }
        for (int i = 0; i < n; i++) {
            if (scanf("%d", &arr[i]) != 1) {
                free(arr);
                return 1;
            }
        }
    }
    
    if (scanf("%d", &k) != 1) {
        free(arr);
        return 0;
    }
    
    int total = n + k;
    arr = (int *)realloc(arr, (size_t)total * sizeof(int));
    
    if (total > 0 && arr == NULL) {
        return 1;
    }
    
    for (int i = n; i < total; i++) {
        if (scanf("%d", &arr[i]) != 1) {
            free(arr);
            return 1;
        }
    }
    
    long long sum = 0;
    for (int i = 0; i < total; i++) {
        sum += arr[i];
    }
    
    printf("Total Elements: %d\n", total);
    printf("Sum: %lld\n", sum);
    
    free(arr);
    return 0;
}
