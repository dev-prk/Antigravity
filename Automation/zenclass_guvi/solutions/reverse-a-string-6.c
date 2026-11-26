#include <stdio.h>
#include <string.h>

int main() {
    char s[1000001];
    if (fgets(s, sizeof(s), stdin)) {
        size_t len = strlen(s);
        if (len > 0 && s[len - 1] == '\n') {
            s[len - 1] = '\0';
            len--;
        }
        for (int i = len - 1; i >= 0; i--) {
            putchar(s[i]);
        }
        putchar('\n');
    }
    return 0;
}
