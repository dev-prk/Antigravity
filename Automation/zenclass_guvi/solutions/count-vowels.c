#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>

int main() {
    int c;
    long long count = 0;
    while ((c = getchar()) != EOF) {
        if (c == '\n') break;
        char lower = tolower(c);
        if (lower == 'a' || lower == 'e' || lower == 'i' || lower == 'o' || lower == 'u') {
            count++;
        }
    }
    printf("%lld\n", count);
    return 0;
}
