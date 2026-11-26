#include <stdio.h>
void countdown(int n) {
    if (n >= 1) {
        printf("%d\n", n);
        countdown(n - 1);
    }
}
int main(void) {
    int N;
    scanf("%d", &N);
    countdown(N);
    return 0;
}
