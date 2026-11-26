#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    char s[101];
    if (fgets(s, sizeof(s), stdin) != NULL) {
        size_t len = strlen(s);
        if (len > 0 && s[len - 1] == '\n') {
            s[len - 1] = '\0';
            len--;
        }
        char result[101];
        size_t j = 0;
        for (size_t i = 0; i < len; i++) {
            if ((i + 1) % 3 != 0) {
                result[j++] = s[i];
            }
        }
        result[j] = '\0';
        printf("%s\n", result);
    }
    return 0;
}
