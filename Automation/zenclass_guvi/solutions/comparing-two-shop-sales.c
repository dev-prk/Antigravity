#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) != 2) {
        return 0;
    }

    int higher;
    if (a >= b) {
        higher = a;
    } else {
        higher = b;
    }

    printf("%d\n", higher);
    return 0;
}
