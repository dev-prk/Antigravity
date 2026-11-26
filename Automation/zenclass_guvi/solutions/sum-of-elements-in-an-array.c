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
    for (int i = 0; i < N; i++) {
        int x;
        if (scanf("%d", &x) != 1) {
            return 1;
        }
        sum += x;
    }
    
    printf("%lld\n", sum);
    return 0;
}
