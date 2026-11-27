#include <stdio.h>
#include <stdlib.h>

int max_func(int a, int b) {
    return (a > b) ? a : b;
}

int min_func(int a, int b) {
    return (a < b) ? a : b;
}

long long maxProductSubarray(int arr[], int n) {
    if (n == 0) return 0;
    
    long long max_prod = arr[0];
    long long min_prod = arr[0];
    long long result = arr[0];
    
    for (int i = 1; i < n; i++) {
        long long current = arr[i];
        long long temp_max = max_prod;
        
        max_prod = max_func(current, max_func(max_prod * current, min_prod * current));
        min_prod = min_func(current, min_func(temp_max * current, min_prod * current));
        
        result = max_func(result, max_prod);
    }
    
    return result;
}

void getInputArray(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
}

int main() {
    int n;
    scanf("%d", &n);
    
    int *arr = (int*)malloc(n * sizeof(int));
    
    getInputArray(arr, n);
    
    long long result = maxProductSubarray(arr, n);
    
    printf("%lld\n", result);
    
    free(arr);
    return 0;
}
