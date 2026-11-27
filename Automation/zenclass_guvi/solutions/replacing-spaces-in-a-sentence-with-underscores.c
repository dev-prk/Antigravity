#include <stdio.h>
int main(void) {
    char sentence[101];
    if (fgets(sentence, 101, stdin) != NULL) {
        for (int i = 0; sentence[i] != '\0'; i++) {
            if (sentence[i] == ' ') {
                sentence[i] = '_';
            }
        }
        printf("%s", sentence);
    }
    return 0;
}
