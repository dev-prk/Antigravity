#include <stdio.h>

int square(int n) {
    return n * n;
}

int main(void) {
    int num;
    scanf("%d", &num);
    int result = square(num);
    printf("%d\n", result);
    return 0;
}
