#include <stdio.h>
int main() {
    int N, M;
    scanf("%d %d", &N, &M);
    int sum = N + M;
    if (sum % 2 == 0) {
        printf("even");
    } else {
        printf("odd");
    }
    return 0;
}
