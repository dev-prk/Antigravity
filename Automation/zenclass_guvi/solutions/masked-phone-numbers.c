#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main() {
    char phone_numbers[10005];
    if (fgets(phone_numbers, sizeof(phone_numbers), stdin) == NULL) {
        return 0;
    }
    
    // Remove trailing newline if present
    size_t len = strlen(phone_numbers);
    if (len > 0 && phone_numbers[len - 1] == '\n') {
        phone_numbers[len - 1] = '\0';
        len--;
    }
    
    if (len == 0) {
        printf("-1");
        return 0;
    }
    
    // Create output buffer
    char *output = (char *)malloc(len * 2 + 1);
    output[0] = '\0';
    
    // Split by spaces
    char *token = strtok(phone_numbers, " ");
    if (token == NULL) {
        printf("-1");
        free(output);
        return 0;
    }
    
    int first = 1;
    while (token != NULL) {
        // Extract only digits from the phone number
        char *digits = (char *)malloc(16);
        int digit_count = 0;
        
        for (int i = 0; token[i] != '\0'; i++) {
            if (isdigit(token[i])) {
                digits[digit_count++] = token[i];
            }
        }
        digits[digit_count] = '\0';
        
        // Build masked version preserving format
        char *masked = (char *)malloc(strlen(token) + 1);
        int j = 0;
        int digit_idx = 0;
        
        for (int i = 0; token[i] != '\0'; i++) {
            if (isdigit(token[i])) {
                if (digit_idx < digit_count - 4) {
                    masked[j++] = '*';
                } else {
                    masked[j++] = token[i];
                }
                digit_idx++;
            } else {
                masked[j++] = token[i];
            }
        }
        masked[j] = '\0';
        
        if (!first) {
            strcat(output, " ");
        }
        first = 0;
        strcat(output, masked);
        
        free(digits);
        free(masked);
        
        token = strtok(NULL, " ");
    }
    
    printf("%s", output);
    free(output);
    
    return 0;
}
