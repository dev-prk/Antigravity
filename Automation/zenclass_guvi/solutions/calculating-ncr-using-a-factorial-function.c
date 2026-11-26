#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

long long factorial(int x) {
    if (x == 0 || x == 1) {
        return 1;
    }
    long long result = 1;
    for (int i = 2; i <= x; i++) {
        result *= i;
    }
    return result;
}

int main(void) {
    int n, r;
    if (scanf("%d %d", &n, &r) != 2) {
        printf("-1\n");
        return 1;
    }
    
    if (n < 0 || r < 0 || r > n) {
        printf("-1\n");
        return 1;
    }
    
    long long fn = factorial(n);
    long long fr = factorial(r);
    long long fnr = factorial(n - r);
    
    long long ncr = fn / (fr * fnr);
    printf("%lld\n", ncr);
    
    return 0;
}
