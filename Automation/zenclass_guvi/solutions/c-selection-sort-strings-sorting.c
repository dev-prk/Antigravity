#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_WORDS 10000
#define MAX_LEN 256

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    char words[MAX_WORDS][MAX_LEN];
    int lengths[MAX_WORDS];
    
    for (int i = 0; i < n; i++) {
        scanf("%s", words[i]);
        lengths[i] = strlen(words[i]);
    }
    
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) {
            if (lengths[j] < lengths[min_idx]) {
                min_idx = j;
            } else if (lengths[j] == lengths[min_idx]) {
                if (strcmp(words[j], words[min_idx]) < 0) {
                    min_idx = j;
                }
            }
        }
        if (min_idx != i) {
            int tmp_len = lengths[i];
            lengths[i] = lengths[min_idx];
            lengths[min_idx] = tmp_len;
            char tmp[MAX_LEN];
            strcpy(tmp, words[i]);
            strcpy(words[i], words[min_idx]);
            strcpy(words[min_idx], tmp);
        }
    }
    
    for (int i = 0; i < n; i++) {
        printf("%s\n", words[i]);
    }
    
    return 0;
}
