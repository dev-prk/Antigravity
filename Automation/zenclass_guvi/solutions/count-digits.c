#include <stdio.h>
#include <stdlib.h>

int main() {
    char n[100];
    if (fgets(n, sizeof(n), stdin) != NULL) {
        int i = 0;
        while (n[i] == ' ') i++;
        if (n[i] == '-') i++;
        int count = 0;
        while (n[i] >= '0' && n[i] <= '9') {
            count++;
            i++;
        }
        printf("%d\n", count);
    }
    return 0;
}
