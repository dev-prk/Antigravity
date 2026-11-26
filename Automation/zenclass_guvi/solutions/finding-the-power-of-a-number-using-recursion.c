#include <stdio.h>

int power(int base, int exp) {
    if (exp == 0) return 1;
    return base * power(base, exp - 1);
}

int main(void) {
    int base, exp;
    if (scanf("%d %d", &base, &exp) == 2) {
        int result = power(base, exp);
        printf("%d", result);
    }
    return 0;
}
