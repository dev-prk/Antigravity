#include <stdio.h>
int main(void) {
    int N;
    scanf("%d", &N);
    float sum = 0.0;
    for (int i = 1; i <= N; i++) {
        sum += 1.0 / i;
    }
    printf("%.2f\n", sum);
    return 0;
}
