#include <stdio.h>
#include <stdlib.h>

void swap_and_diff(int *x, int *y) {
    int temp = *x;
    *x = *y;
    *y = abs(temp - *y);
}

int main() {
    int x, y;
    scanf("%d %d", &x, &y);
    swap_and_diff(&x, &y);
    printf("%d %d\n", x, y);
    return 0;
}
