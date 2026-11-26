#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int a, b, temp;
    if (scanf("%d %d", &a, &b) != 2) {
        return 0;
    }
    temp = a;
    a = b;
    b = temp;
    printf("%d\n%d\n", a, b);
    return 0;
}
