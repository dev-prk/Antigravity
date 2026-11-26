#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    char word[1000001];
    char ch;
    
    if (scanf("%1000000s %c", word, &ch) != 2) {
        return 1;
    }
    
    int count = 0;
    for (int i = 0; word[i] != '\0'; i++) {
        if (word[i] == ch) {
            count++;
        }
    }
    
    printf("%d\n", count);
    
    return 0;
}
