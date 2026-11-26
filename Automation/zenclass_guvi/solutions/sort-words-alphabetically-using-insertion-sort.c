#include <stdio.h>
#include <string.h>

#define MAX_WORDS 100
#define MAX_LEN 101

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    char words[MAX_WORDS][MAX_LEN];
    
    for (int i = 0; i < n; i++) {
        scanf("%100s", words[i]);
    }
    
    for (int i = 1; i < n; i++) {
        char key[MAX_LEN];
        strcpy(key, words[i]);
        int j = i - 1;
        
        while (j >= 0 && strcmp(words[j], key) > 0) {
            strcpy(words[j + 1], words[j]);
            j--;
        }
        strcpy(words[j + 1], key);
    }
    
    for (int i = 0; i < n; i++) {
        printf("%s\n", words[i]);
    }
    
    return 0;
}
