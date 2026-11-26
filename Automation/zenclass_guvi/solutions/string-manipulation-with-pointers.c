#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void reverse_string(char *str) {
    if (str == NULL || *str == '\0') return;
    
    char *start = str;
    char *end = str;
    
    while (*end != '\0') {
        end++;
    }
    end--;
    
    while (start < end) {
        char temp = *start;
        *start = *end;
        *end = temp;
        start++;
        end--;
    }
}

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n <= 0) {
        return 0;
    }
    
    // Consume remaining newline after scanf
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
    
    char **strings = (char **)malloc(n * sizeof(char *));
    if (strings == NULL) {
        return 1;
    }
    
    // Read all strings
    for (int i = 0; i < n; i++) {
        strings[i] = NULL;
        char buffer[10000];
        if (fgets(buffer, sizeof(buffer), stdin) != NULL) {
            // Remove trailing newline
            size_t len = strlen(buffer);
            while (len > 0 && (buffer[len-1] == '\n' || buffer[len-1] == '\r')) {
                buffer[--len] = '\0';
            }
            
            strings[i] = (char *)malloc((len + 1) * sizeof(char));
            if (strings[i] != NULL) {
                strcpy(strings[i], buffer);
            }
        }
    }
    
    // Reverse each string
    for (int i = 0; i < n; i++) {
        if (strings[i] != NULL) {
            reverse_string(strings[i]);
        }
    }
    
    // Swap first and last string
    if (n >= 2) {
        char *temp = strings[0];
        strings[0] = strings[n-1];
        strings[n-1] = temp;
    }
    
    // Print the modified list
    for (int i = 0; i < n; i++) {
        if (strings[i] != NULL) {
            printf("%s\n", strings[i]);
        }
    }
    
    // Free allocated memory
    for (int i = 0; i < n; i++) {
        if (strings[i] != NULL) {
            free(strings[i]);
        }
    }
    free(strings);
    
    return 0;
}
