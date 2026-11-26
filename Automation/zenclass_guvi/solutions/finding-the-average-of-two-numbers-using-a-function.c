#include <stdio.h>

float averageOfTwo(int a, int b) {
    return (a + b) / 2.0;
}

int main(void) {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%.2f\n", averageOfTwo(a, b));
    return 0;
}
