#include <stdio.h>
#include <string.h>
#include <ctype.h>
 
int main(void) {
    int vowels = 0;
    char word[512];
    scanf("%s", word);
    
    for (int i = 0; word[i] != '\0'; i++) {
        char c = tolower(word[i]);
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {
            vowels++;
        }
    }
    
    printf("%d\n", vowels);
    return 0;
}
