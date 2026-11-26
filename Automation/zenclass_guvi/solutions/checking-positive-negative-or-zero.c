#include <stdio.h>

int main(void) {
    int num;
    if (scanf("%d", &num) != 1) {
        return 0;
    }
    if (num > 0) {
        printf("Positive\n");
    } else if (num < 0) {
        printf("Negative\n");
    } else {
        printf("Zero\n");
    }
    return 0;
}
