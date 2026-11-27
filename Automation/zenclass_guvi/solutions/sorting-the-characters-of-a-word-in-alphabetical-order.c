#include <stdio.h>
int main(void) {
    char word[100];
    scanf("%s", word);
    
    int len = 0;
    while (word[len] != '\0') {
        len++;
    }
    
    for (int i = 0; i < len - 1; i++) {
        for (int j = 0; j < len - i - 1; j++) {
            if (word[j] > word[j + 1]) {
                char temp = word[j];
                word[j] = word[j + 1];
                word[j + 1] = temp;
            }
        }
    }
    
    printf("%s\n", word);
    return 0;
}
