#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    char sentence[101];
    int letters = 0;
    int digits = 0;
    int spaces = 0;

    if (fgets(sentence, sizeof(sentence), stdin) != NULL) {
        for (int i = 0; sentence[i] != '\0'; i++) {
            if ((sentence[i] >= 'a' && sentence[i] <= 'z') ||
                (sentence[i] >= 'A' && sentence[i] <= 'Z')) {
                letters++;
            } else if (sentence[i] >= '0' && sentence[i] <= '9') {
                digits++;
            } else if (sentence[i] == ' ') {
                spaces++;
            }
        }
    }

    printf("%d\n%d\n%d\n", letters, digits, spaces);

    return 0;
}
