#include <stdio.h>
#include <string.h>

int main() {
    char str[1000];
    fgets(str, sizeof(str), stdin);
    
    // Remove trailing newline if present
    int len = strlen(str);
    if (len > 0 && str[len-1] == '\n') {
        str[len-1] = '\0';
        len--;
    }
    
    // Remove surrounding quotes if present
    if (len >= 2 && str[0] == '"' && str[len-1] == '"') {
        memmove(str, str+1, len-2);
        str[len-2] = '\0';
        len -= 2;
    }
    
    // Reverse the string in-place
    int i = 0, j = len - 1;
    while (i < j) {
        char temp = str[i];
        str[i] = str[j];
        str[j] = temp;
        i++;
        j--;
    }
    
    printf("Reversed string: \"%s\"\n", str);
    
    return 0;
}
