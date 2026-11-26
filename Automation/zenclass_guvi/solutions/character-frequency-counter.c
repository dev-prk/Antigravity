#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main() {
    char *input = NULL;
    size_t size = 0;
    
    if (getline(&input, &size, stdin) == -1) {
        free(input);
        return 0;
    }
    
    int freq[26] = {0};
    
    for (int i = 0; input[i] != '\0'; i++) {
        char c = input[i];
        if (isalpha(c)) {
            c = tolower(c);
            freq[c - 'a']++;
        }
    }
    
    typedef struct {
        char ch;
        int count;
    } CharCount;
    
    CharCount chars[26];
    int n = 0;
    
    for (int i = 0; i < 26; i++) {
        if (freq[i] > 0) {
            chars[n].ch = 'a' + i;
            chars[n].count = freq[i];
            n++;
        }
    }
    
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (chars[j].count < chars[j + 1].count ||
                (chars[j].count == chars[j + 1].count && chars[j].ch > chars[j + 1].ch)) {
                CharCount temp = chars[j];
                chars[j] = chars[j + 1];
                chars[j + 1] = temp;
            }
        }
    }
    
    for (int i = 0; i < n; i++) {
        printf("%c: %d\n", chars[i].ch, chars[i].count);
    }
    
    free(input);
    return 0;
}
