#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int fibonacci(int n) {
    if (n == 1) {
        return 0;
    }
    if (n == 2) {
        return 1;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main(void) {
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    printf("%d\n", fibonacci(n));
    return 0;
}
