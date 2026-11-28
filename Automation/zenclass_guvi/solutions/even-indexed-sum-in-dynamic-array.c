#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    if (n <= 0) {
        return 0;
    }
    
    int *arr = (int*)malloc(n * sizeof(int));
    if (arr == NULL) return 1;
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    int sum = 0;
    for (int i = 0; i < n; i += 2) {
        sum += arr[i];
    }
    
    arr[0] = sum;
    
    for (int i = 0; i < n; i++) {
        if (i > 0) printf(" ");
        printf("%d", arr[i]);
    }
    printf(" \n");
    
    free(arr);
    return 0;
}
