#include <stdio.h>
int sumNatural(int n) {
    if (n == 0) {
        return 0;
    }
    return n + sumNatural(n - 1);
}
int main(void) {
    int N;
    scanf("%d", &N);
    printf("%d\n", sumNatural(N));
    return 0;
}
