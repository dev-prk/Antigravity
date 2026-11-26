#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int num;
    scanf("%d", &num);
    int bits[4];
    int temp = num;
    for (int i = 0; i < 4; ++i) {
        bits[3 - i] = temp % 2;
        temp /= 2;
    }
    for (int i = 0; i < 4; ++i) {
        printf("%d", bits[i]);
    }
    return 0;
}
