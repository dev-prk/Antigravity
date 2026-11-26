#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

long long factorial_tail(int n, long long acc) {
    if (n == 0 || n == 1) {
        return acc;
    }
    return factorial_tail(n - 1, n * acc);
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    
    if (n < 0) {
        printf("-1\n");
        return 0;
    }
    
    printf("%lld\n", factorial_tail(n, 1));
    
    return 0;
}
