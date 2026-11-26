#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n < 0) {
        return 1;
    }
    
    getchar(); // consume newline after n
    
    char **strings = NULL;
    if (n > 0) {
        strings = malloc(n * sizeof(char *));
        if (!strings) return 1;
    }
    
    for (int i = 0; i < n; i++) {
        char buffer[10000];
        if (fgets(buffer, sizeof(buffer), stdin) == NULL) {
            // clean up already allocated memory
            for (int j = 0; j < i; j++) {
                free(strings[j]);
            }
            free(strings);
            return 1;
        }
        
        // Remove trailing newline
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len - 1] == '\n') {
            buffer[len - 1] = '\0';
            len--;
        }
        
        strings[i] = malloc(len + 1);
        if (!strings[i]) {
            for (int j = 0; j < i; j++) {
                free(strings[j]);
            }
            free(strings);
            return 1;
        }
        strcpy(strings[i], buffer);
    }
    
    int a_count = 0, e_count = 0, i_count = 0, o_count = 0, u_count = 0;
    
    for (int i = 0; i < n; i++) {
        for (int j = 0; strings[i][j] != '\0'; j++) {
            char c = tolower(strings[i][j]);
            switch (c) {
                case 'a': a_count++; break;
                case 'e': e_count++; break;
                case 'i': i_count++; break;
                case 'o': o_count++; break;
                case 'u': u_count++; break;
            }
        }
    }
    
    printf("a: %d, e: %d, i: %d, o: %d, u: %d\n", a_count, e_count, i_count, o_count, u_count);
    
    for (int i = 0; i < n; i++) {
        free(strings[i]);
    }
    free(strings);
    
    return 0;
}
