#include <stdio.h>

int main(void) {
    int x;
    if (scanf("%d", &x) != 1) return 0;

    int a = x++;   // post-increment: use then increment
    int b = ++x;   // pre-increment: increment then use

    printf("%d\n%d\n%d\n", a, b, x);
    return 0;
}
