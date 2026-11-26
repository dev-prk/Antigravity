#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int N;
    if (scanf("%d", &N) != 1 || N < 1) {
        return 1;
    }
    for (int i = 1; i <= N; i++) {
        printf("%d", i * i);
        if (i < N) {
            printf(" ");
        }
    }
    printf("\n");
    return 0;
}
