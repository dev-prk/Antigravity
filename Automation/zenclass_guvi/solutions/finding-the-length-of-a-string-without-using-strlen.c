#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    char word[1000];
    if (scanf("%999s", word) != 1) {
        printf("0\n");
        return 0;
    }
    
    int length = 0;
    while (word[length] != '\0') {
        length++;
    }
    
    printf("%d\n", length);
    return 0;
}
