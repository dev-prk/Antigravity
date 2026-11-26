#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    char word1[1000001], word2[1000001];
    if (scanf("%1000000s%1000000s", word1, word2) != 2) {
        printf("Not Anagram\n");
        return 0;
    }
    
    int freq[26] = {0};
    
    size_t len1 = strlen(word1);
    for (size_t i = 0; i < len1; i++) {
        freq[word1[i] - 'a']++;
    }
    
    size_t len2 = strlen(word2);
    for (size_t i = 0; i < len2; i++) {
        freq[word2[i] - 'a']--;
    }
    
    int isAnagram = 1;
    for (int i = 0; i < 26; i++) {
        if (freq[i] != 0) {
            isAnagram = 0;
            break;
        }
    }
    
    if (isAnagram) {
        printf("Anagram\n");
    } else {
        printf("Not Anagram\n");
    }
    
    return 0;
}
