#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int fib[8];
    fib[0] = 0;
    fib[1] = 1;
    for (int i = 2; i < 8; i++) {
        fib[i] = fib[i-1] + fib[i-2];
    }
    int sum = 0;
    for (int i = 0; i < 8; i++) {
        sum += fib[i];
    }
    for (int i = 0; i < 8; i++) {
        printf("%d", fib[i]);
        if (i < 7) printf(" ");
    }
    printf("\n%d\n", sum);
    return 0;
}
