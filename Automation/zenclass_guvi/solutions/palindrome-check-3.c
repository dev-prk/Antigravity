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
        int is_palindrome = 1;
        for (size_t i = 0; i < len / 2; i++) {
            if (s[i] != s[len - 1 - i]) {
                is_palindrome = 0;
                break;
            }
        }
        printf("%s\n", is_palindrome ? "Yes" : "No");
    }
    return 0;
}
