#include <stdio.h>
#include <stdlib.h>

int main(void) {
    long long N;
    if (scanf("%lld", &N) != 1) return 0;
    for (long long i = 0; i < N; ++i) {
        long long R, S, E;
        if (scanf("%lld %lld %lld", &R, &S, &E) != 3) break;
        if (S > E) {
            printf("Invalid booking\n");
            continue;
        }
        long long days = E - S + 1;
        long long rate = (R + 1) * 50;          // nightly rate
        long long total = days * rate;
        printf("%lld\n", total);
    }
    return 0;
}
