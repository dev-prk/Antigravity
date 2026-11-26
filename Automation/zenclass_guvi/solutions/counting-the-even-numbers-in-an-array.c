#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int N;
    if (scanf("%d", &N) != 1) {
        return 1;
    }
    
    int *arr = malloc(N * sizeof(int));
    if (arr == NULL) {
        return 1;
    }
    
    for (int i = 0; i < N; i++) {
        if (scanf("%d", &arr[i]) != 1) {
            free(arr);
            return 1;
        }
    }
    
    int count = 0;
    for (int i = 0; i < N; i++) {
        if (arr[i] % 2 == 0) {
            count++;
        }
    }
    
    printf("%d\n", count);
    
    free(arr);
    return 0;
}
