#include <stdio.h>

int isValidTriangle(int a, int b, int c) {
    if (a <= 0 || b <= 0 || c <= 0) {
        return 0;
    }
    return ((long long)a + b > c) &&
           ((long long)a + c > b) &&
           ((long long)b + c > a);
}

int main(void) {
    int a, b, c;
    if (scanf("%d %d %d", &a, &b, &c) != 3) {
        return 0;
    }
    if (isValidTriangle(a, b, c)) {
        printf("Valid\n");
    } else {
        printf("Not Valid\n");
    }
    return 0;
}
