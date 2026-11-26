#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int multiply(int a, int b) {
    if (b == 0) {
        return 0;
    }
    return a + multiply(a, b - 1);
}

int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) != 2) {
        return 1;
    }
    printf("%d\n", multiply(a, b));
    return 0;
}
