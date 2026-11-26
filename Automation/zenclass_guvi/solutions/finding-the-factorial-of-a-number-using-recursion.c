#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

long long factorial(int n) {
    if (n == 0 || n == 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main(void) {
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    
    if (n < 0 || n > 10) {
        return 1;
    }
    
    printf("%lld\n", factorial(n));
    return 0;
}
