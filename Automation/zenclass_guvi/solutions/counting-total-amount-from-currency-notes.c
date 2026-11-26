#include <stdio.h>
int main(void) {
    int n500, n200, n100;
    scanf("%d %d %d", &n500, &n200, &n100);
    int total = n500 * 500 + n200 * 200 + n100 * 100;
    printf("%d\n", total);
    return 0;
}
