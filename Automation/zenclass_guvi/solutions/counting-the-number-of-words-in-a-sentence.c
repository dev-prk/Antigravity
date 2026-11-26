#include <stdio.h>
#include <string.h>

int main(void) {
    char sentence[1000];
    if (fgets(sentence, sizeof(sentence), stdin) == NULL) {
        printf("0\n");
        return 0;
    }
    
    int len = strlen(sentence);
    if (len > 0 && sentence[len - 1] == '\n') {
        sentence[len - 1] = '\0';
        len--;
    }
    
    if (len == 0) {
        printf("0\n");
        return 0;
    }
    
    int count = 0;
    int i;
    for (i = 0; i < len; i++) {
        if (sentence[i] != ' ') {
            count++;
            while (i < len && sentence[i] != ' ') {
                i++;
            }
            i--;
        }
    }
    
    printf("%d\n", count);
    return 0;
}
