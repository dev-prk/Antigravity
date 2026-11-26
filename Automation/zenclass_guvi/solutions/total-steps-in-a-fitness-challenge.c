#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int N;
    if (scanf("%d", &N) != 1) {
        return 1;
    }
    
    long long sum = 0;
    int i = 1;
    while (i <= N) {
        sum += i;
        i++;
    }
    
    printf("%lld\n", sum);
    return 0;
}
