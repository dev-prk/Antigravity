#include <stdio.h>

int main() {
    int n;
    scanf("%d", &n);
    unsigned long long factorial = 1;
    if (n == 0 || n == 1) {
        factorial = 1;
    } else {
        for (int i = 2; i <= n; i++) {
            factorial *= i;
        }
    }
    printf("%llu\n", factorial);
    return 0;
}
