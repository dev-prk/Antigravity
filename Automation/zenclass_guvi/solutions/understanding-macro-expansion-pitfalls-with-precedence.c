#include <stdio.h>
#define SQUARE(x) x * x

int main(void) {
    int a, b;
    scanf("%d %d", &a, &b);
    int result = SQUARE(a + b);
    int expected = (a + b) * (a + b);
    printf("%d\n%d\n", result, expected);
    return 0;
}
