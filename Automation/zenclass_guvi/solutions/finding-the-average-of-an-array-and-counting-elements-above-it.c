#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int N;
    if (scanf("%d", &N) != 1 || N < 1) {
        return 0;
    }
    
    int *arr = (int *)malloc(N * sizeof(int));
    if (arr == NULL) {
        return 0;
    }
    
    long long sum = 0;
    for (int i = 0; i < N; i++) {
        if (scanf("%d", &arr[i]) != 1) {
            free(arr);
            return 0;
        }
        sum += arr[i];
    }
    
    float avg = (float)sum / (float)N;
    printf("%.2f\n", avg);
    
    int count = 0;
    for (int i = 0; i < N; i++) {
        if (arr[i] > avg) {
            count++;
        }
    }
    printf("%d\n", count);
    
    free(arr);
    return 0;
}
