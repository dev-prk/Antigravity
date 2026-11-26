#include <stdio.h>

int main(void) {
    char word[100];

    if (scanf("%99s", word) != 1) {
        return 0;
    }

    int length = 0;
    while (word[length] != '\0') {
        length++;
    }

    int flag = 0;
    for (int i = 0; i < length / 2; i++) {
        if (word[i] != word[length - 1 - i]) {
            flag = 1;
            break;
        }
    }

    if (flag == 0) {
        printf("Palindrome\n");
    } else {
        printf("Not Palindrome\n");
    }

    return 0;
}
