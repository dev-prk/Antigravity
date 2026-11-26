#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int a, b, c;
    if (scanf("%d %d %d", &a, &b, &c) == 3) {
        int result = (a > b) && (c > 0);
        printf("%d\n", result);
    }
    return 0;
}
