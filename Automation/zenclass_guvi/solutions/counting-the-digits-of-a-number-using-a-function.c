#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int countDigits(int n) {
    if (n == 0) {
        return 1;
    }
    int count = 0;
    while (n > 0) {
        n /= 10;
        count++;
    }
    return count;
}

int main(void) {
    int num;
    if (scanf("%d", &num) != 1) {
        return 1;
    }
    if (num < 0) {
        num = -num;
    }
    int result = countDigits(num);
    printf("%d\n", result);
    return 0;
}
