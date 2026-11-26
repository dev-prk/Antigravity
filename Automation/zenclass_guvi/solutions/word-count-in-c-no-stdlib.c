#include <stdio.h>

int count_words(char arr[]) {
    int count = 0;
    int in_word = 0;
    
    for (int i = 0; arr[i] != '\0'; i++) {
        if (arr[i] != ' ') {
            if (!in_word) {
                in_word = 1;
                count++;
            }
        } else {
            in_word = 0;
        }
    }
    
    return count;
}

int main() {
    char arr[100];
    fgets(arr, 100, stdin);
    
    int result = count_words(arr);
    printf("%d\n", result);
    
    return 0;
}
