#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char *sentence = NULL;
    size_t len = 0;
    ssize_t read;
    
    read = getline(&sentence, &len, stdin);
    
    if (read <= 0) {
        free(sentence);
        return 0;
    }
    
    if (sentence[read - 1] == '\n') {
        sentence[read - 1] = '\0';
        read--;
    }
    
    if (read == 0) {
        free(sentence);
        return 0;
    }
    
    int word_count = 0;
    char **words = NULL;
    int current_word_len = 0;
    
    for (int i = 0; i <= read; i++) {
        if (sentence[i] == ' ' || sentence[i] == '\0') {
            if (current_word_len > 0) {
                words = realloc(words, (word_count + 1) * sizeof(char *));
                words[word_count] = malloc((current_word_len + 1) * sizeof(char));
                strncpy(words[word_count], sentence + i - current_word_len, current_word_len);
                words[word_count][current_word_len] = '\0';
                word_count++;
                current_word_len = 0;
            }
        } else {
            current_word_len++;
        }
    }
    
    for (int i = word_count - 1; i >= 0; i--) {
        printf("%s", words[i]);
        if (i > 0) {
            printf(" ");
        }
    }
    printf("\n");
    
    for (int i = 0; i < word_count; i++) {
        free(words[i]);
    }
    free(words);
    free(sentence);
    
    return 0;
}
