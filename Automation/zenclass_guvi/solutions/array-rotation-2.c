#include <stdio.h>
#include <stdlib.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    if (n <= 0) {
        return 0;
    }
    
    int *arr = (int*)malloc(n * sizeof(int));
    if (arr == NULL) return 0;
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    int k;
    scanf("%d", &k);
    
    // Handle negative k or k larger than n
    if (k < 0) {
        k = k % n + n;
    }
    k = k % n;
    
    int *result = (int*)malloc(n * sizeof(int));
    if (result == NULL) {
        free(arr);
        return 0;
    }
    
    // Copy elements from k to end first
    int resultIndex = 0;
    for (int i = k; i < n; i++) {
        result[resultIndex++] = arr[i];
    }
    
    // Copy elements from start to k
    for (int i = 0; i < k; i++) {
        result[resultIndex++] = arr[i];
    }
    
    // Print the result
    for (int i = 0; i < n; i++) {
        printf("%d ", result[i]);
    }
    printf("\n");
    
    free(arr);
    free(result);
    
    return 0;
}
