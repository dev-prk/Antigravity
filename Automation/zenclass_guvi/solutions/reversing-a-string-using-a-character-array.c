#include <stdio.h>
int main(void) {
    char word[100];
    scanf("%s", word);
    
    int length = 0;
    while (word[length] != '\0') {
        length++;
    }
    
    for (int i = length - 1; i >= 0; i--) {
        printf("%c", word[i]);
    }
    
    return 0;
}
