#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int isDivisible(int n) {
    if (n % 3 == 0 && n % 5 == 0) {
        return 1;
    }
    return 0;
}

int main(void) {
    int num;
    if (scanf("%d", &num) != 1) {
        printf("Not Divisible\n");
        return 0;
    }
    if (isDivisible(num)) {
        printf("Divisible\n");
    } else {
        printf("Not Divisible\n");
    }
    return 0;
}
