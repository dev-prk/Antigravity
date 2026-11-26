#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) != 2) {
        return 1;
    }
    int int_div = a / b;
    double float_div = (double)a / b;
    printf("%d\n", int_div);
    printf("%.2f\n", float_div);
    return 0;
}
