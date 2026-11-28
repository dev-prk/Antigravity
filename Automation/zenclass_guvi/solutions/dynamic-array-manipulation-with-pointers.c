#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

void manipulate_array(int *arr, int n) {
    if (n <= 1) {
        return;
    }
    
    for (int i = 0; i < n - 1; i++) {
        arr[i] += arr[i + 1];
    }
    
    int temp = arr[0];
    arr[0] = arr[n - 1];
    arr[n - 1] = temp;
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    
    if (n <= 0) {
        printf("\n");
        return 0;
    }
    
    int *arr = (int *)malloc(n * sizeof(int));
    if (arr == NULL) {
        return 1;
    }
    
    for (int i = 0; i < n; i++) {
        arr[i] = i * i;
    }
    
    manipulate_array(arr, n);
    
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    
    free(arr);
    
    return 0;
}
