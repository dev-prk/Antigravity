#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>

int is_vowel(char c) {
    c = tolower((unsigned char)c);
    return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u';
}

int main(void) {
    char input[100000];
    if (!fgets(input, sizeof(input), stdin)) {
        return 0;
    }
    
    size_t len = strlen(input);
    while (len > 0 && (input[len-1] == '\n' || input[len-1] == '\r')) {
        input[--len] = '\0';
    }
    
    char *str = input;
    if (len >= 2 && input[0] == '"' && input[len-1] == '"') {
        str = input + 1;
        input[len-1] = '\0';
    }
    
    int vowels = 0;
    int consonants = 0;
    
    for (size_t i = 0; i < strlen(str); i++) {
        char c = str[i];
        if (isalpha((unsigned char)c)) {
            if (is_vowel(c)) {
                vowels++;
            } else {
                consonants++;
            }
        }
    }
    
    printf("Vowels: %d\n", vowels);
    printf("Consonants: %d\n", consonants);
    
    return 0;
}
