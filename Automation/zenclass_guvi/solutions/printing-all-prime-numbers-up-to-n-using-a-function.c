#include <stdio.h>
#include <stdbool.h>

int isPrime(int n) {
    if (n < 2) {
        return 0;
    }
    for (int i = 2; i < n; i++) {
        if (n % i == 0) {
            return 0;
        }
    }
    return 1;
}

int main(void) {
    int N;
    scanf("%d", &N);
    
    int first = 1;
    for (int i = 2; i <= N; i++) {
        if (isPrime(i)) {
            if (!first) {
                printf(" ");
            }
            printf("%d", i);
            first = 0;
        }
    }
    printf("\n");
    
    return 0;
}
