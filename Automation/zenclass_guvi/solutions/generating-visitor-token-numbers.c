#include <stdio.h>

int main(void) {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    for (int i = 1; i <= N; i++) {
        printf("%d\n", i);
    }
    return 0;
}
