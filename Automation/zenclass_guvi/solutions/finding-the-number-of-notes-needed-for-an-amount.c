#include <stdio.h>
int main(void) {
    int amount, r500, r100, r50, r10;
    scanf("%d", &amount);
    r500 = amount / 500;
    amount %= 500;
    r100 = amount / 100;
    amount %= 100;
    r50 = amount / 50;
    amount %= 50;
    r10 = amount / 10;
    printf("%d\n%d\n%d\n%d\n", r500, r100, r50, r10);
    return 0;
}
