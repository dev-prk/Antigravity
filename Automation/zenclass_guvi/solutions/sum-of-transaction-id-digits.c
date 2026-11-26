#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    char input[1000];
    if (fgets(input, sizeof(input), stdin) == NULL) {
        return 0;
    }
    
    int sum = 0;
    for (int i = 0; input[i] != '\0'; i++) {
        if (input[i] >= '0' && input[i] <= '9') {
            sum += input[i] - '0';
        }
    }
    
    printf("Sum of digits: %d", sum);
    if (input[strlen(input)-1] == '\n') {
        printf("\n");
    }
    return 0;
}
