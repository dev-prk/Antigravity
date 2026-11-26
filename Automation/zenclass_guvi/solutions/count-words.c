#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int c;
    int in_word = 0;
    int count = 0;

    while ((c = getchar()) != EOF) {
        if (c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v' || c == '\f') {
            in_word = 0;
        } else if (!in_word) {
            count++;
            in_word = 1;
        }
    }

    printf("%d\n", count);
    return 0;
}
