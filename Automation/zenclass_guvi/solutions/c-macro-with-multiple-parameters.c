#include <stdio.h>

#define COMPUTE(a, b, c, d) \
    do { \
        int temp1 = (a) * (b); \
        printf("Intermediate result of a * b: %d\n", temp1); \
        int temp2 = temp1 + (c); \
        printf("Intermediate result of a * b + c: %d\n", temp2); \
        int result = temp2 / (d); \
        printf("Final result of (a * b + c) / d: %d\n", result); \
    } while(0)

int main() {
    int a, b, c, d;
    scanf("%d", &a);
    scanf("%d", &b);
    scanf("%d", &c);
    scanf("%d", &d);
    COMPUTE(a, b, c, d);
    return 0;
}
