#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) != 2) {
        return 1;
    }
    while (b != 0) {
        int temp = a % b;
        a = b;
        b = temp;
    }
    printf("%d\n", a);
    return 0;
}
