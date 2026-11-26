#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main() {
    char code[100];
    if (fgets(code, sizeof(code), stdin) == NULL) {
        printf("Invalid promotional code.\n");
        return 0;
    }
    
    size_t len = strlen(code);
    if (len > 0 && code[len - 1] == '\n') {
        code[len - 1] = '\0';
        len--;
    }
    
    if (len != 10) {
        printf("Invalid promotional code.\n");
        return 0;
    }
    
    int has_digit = 0;
    int has_upper = 0;
    
    for (int i = 0; i < 10; i++) {
        if (isdigit(code[i])) {
            has_digit = 1;
        } else if (isupper(code[i])) {
            has_upper = 1;
        }
    }
    
    if (has_digit && has_upper) {
        printf("Valid promotional code.\n");
    } else {
        printf("Invalid promotional code.\n");
    }
    
    return 0;
}
