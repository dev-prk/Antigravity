#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    if (N <= 0) {
        return 0;
    }
    int *arr = (int *)malloc(N * sizeof(int));
    if (!arr) return 0;
    for (int i = 0; i < N; ++i) {
        scanf("%d", &arr[i]);
    }
    for (int i = N - 1; i >= 0; --i) {
        printf("%d", arr[i]);
        if (i > 0) printf(" ");
    }
    free(arr);
    return 0;
}
