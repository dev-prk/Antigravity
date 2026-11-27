#include <stdio.h>
int main(void) {
    int N, temp, max;
    scanf("%d", &N);
    scanf("%d", &temp);
    max = temp;
    for (int i = 1; i < N; i++) {
        scanf("%d", &temp);
        if (temp > max) {
            max = temp;
        }
    }
    printf("%d\n", max);
    return 0;
}
