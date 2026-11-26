#include <stdio.h>

int main(void) {
    long long a, b, c, d;
    if (scanf("%lld %lld %lld %lld", &a, &b, &c, &d) != 4) return 0;
    long long result = a + b * c - d / 2;
    printf("%lld", result);
    return 0;
}
