#include <stdio.h>
#include <stdlib.h>

int main() {
    int a, b, c;
    if (scanf("%d %d %d", &a, &b, &c) != 3) return 0;
    int largest;
    if (a > b) {
        if (a > c) largest = a;
        else largest = c;
    } else {
        if (b > c) largest = b;
        else largest = c;
    }
    printf("%d\n", largest);
    return 0;
}
