#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

void replace_vowels(char arr[], char replacement) {
    for (int i = 0; arr[i] != '\0'; i++) {
        char c = arr[i];
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
            c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') {
            arr[i] = replacement;
        }
    }
}

int main() {
    char arr[105];
    char replacement;
    
    if (fgets(arr, sizeof(arr), stdin) == NULL) {
        return 1;
    }
    
    // Remove trailing newline if present
    size_t len = strlen(arr);
    if (len > 0 && arr[len - 1] == '\n') {
        arr[len - 1] = '\0';
    }
    
    if (scanf(" %c", &replacement) != 1) {
        return 1;
    }
    
    replace_vowels(arr, replacement);
    
    printf("%s\n", arr);
    
    return 0;
}
