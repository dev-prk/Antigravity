#include <stdio.h>
int main(void) {
    char lower;
    if (scanf(" %c", &lower) == 1) {
        char upper = lower - 32;
        printf("%c", upper);
    }
    return 0;
}
