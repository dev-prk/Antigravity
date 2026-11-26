#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int N;
    if (scanf("%d", &N) != 1) {
        return 1;
    }
    
    if (N <= 0) {
        printf("-1\n");
        return 0;
    }
    
    int *arr = (int *)malloc(N * sizeof(int));
    if (arr == NULL) {
        return 1;
    }
    
    for (int i = 0; i < N; i++) {
        scanf("%d", &arr[i]);
    }
    
    int largest = arr[0];
    for (int i = 1; i < N; i++) {
        if (arr[i] > largest) {
            largest = arr[i];
        }
    }
    
    printf("%d\n", largest);
    
    free(arr);
    return 0;
}
