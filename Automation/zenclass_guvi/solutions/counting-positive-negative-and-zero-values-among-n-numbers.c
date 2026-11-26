#include <stdio.h>
int main(void) {
    int N, num, positive = 0, negative = 0, zero = 0;
    scanf("%d", &N);
    for (int i = 0; i < N; i++) {
        scanf("%d", &num);
        if (num > 0) {
            positive++;
        } else if (num < 0) {
            negative++;
        } else {
            zero++;
        }
    }
    printf("%d\n%d\n%d\n", positive, negative, zero);
    return 0;
}
