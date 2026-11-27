#include <stdio.h>
int main(void) {
    int N, num, profit = 0, loss = 0, zero = 0;
    scanf("%d", &N);
    for (int i = 0; i < N; i++) {
        scanf("%d", &num);
        if (num > 0) {
            profit++;
        } else if (num < 0) {
            loss++;
        } else {
            zero++;
        }
    }
    printf("%d\n%d\n%d\n", profit, loss, zero);
    return 0;
}
