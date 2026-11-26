#include <stdio.h>
int main(void) {
    int a = 0, b = 1, c, d, e;
    c = a + b;
    d = b + c;
    e = c + d;
    printf("%d %d %d %d %d\n", a, b, c, d, e);
    return 0;
}
