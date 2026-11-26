#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    if (n <= 0) {
        int x, y;
        scanf("%d%d", &x, &y);
        printf("0\n");
        return 0;
    }
    
    long long *arr = (long long *)malloc(n * sizeof(long long));
    for (int i = 0; i < n; i++) {
        scanf("%lld", &arr[i]);
    }
    
    int x, y;
    scanf("%d%d", &x, &y);
    
    // Step 1: Element Replacement
    for (int i = 0; i < n; i++) {
        if (arr[i] % x == 0) {
            arr[i] = y;
        }
    }
    
    // Step 2: Incremental Sum Update
    for (int i = 0; i < n - 1; i++) {
        arr[i] = arr[i] + arr[i + 1];
    }
    
    // Step 3: Find Maximum Value
    long long maxVal = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > maxVal) {
            maxVal = arr[i];
        }
    }
    
    printf("%lld\n", maxVal);
    
    free(arr);
    return 0;
}
