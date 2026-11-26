#include <stdio.h>

int main(void) {
    int x;
    int innerVal;

    if (scanf("%d %d", &x, &innerVal) != 2) {
        return 0;
    }

    printf("%d\n", x);

    {
        int x = innerVal;
        printf("%d\n", x);
    }

    printf("%d\n", x);

    return 0;
}
