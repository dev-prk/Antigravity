#include <stdio.h>
int main() {
    int N;
    scanf("%d", &N);
    unsigned long long result = 1;
    if (N < 0) {
        printf("0\n");
        return 0;
    }
    for (int i = 2; i <= N; i++) {
        result *= i;
    }
    printf("%llu\n", result);
    return 0;
}
