#include <stdio.h>
#include <string.h>

int main() {
    char id[100];
    if (fgets(id, sizeof(id), stdin) != NULL) {
        size_t len = strlen(id);
        if (len > 0 && id[len - 1] == '\n') {
            id[len - 1] = '\0';
            len--;
        }
        printf("Reversed number: ");
        for (int i = len - 1; i >= 0; i--) {
            putchar(id[i]);
        }
        putchar('\n');
    }
    return 0;
}
