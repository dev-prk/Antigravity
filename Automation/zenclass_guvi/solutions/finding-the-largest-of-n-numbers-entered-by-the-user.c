#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    if (N <= 0) {
        printf("-1\n");
        return 0;
    }
    
    int max;
    if (scanf("%d", &max) != 1) return 0;
    
    for (int i = 1; i < N; i++) {
        int num;
        if (scanf("%d", &num) == 1) {
            if (num > max) {
                max = num;
            }
        }
    }
    
    printf("%d\n", max);
    return 0;
}
