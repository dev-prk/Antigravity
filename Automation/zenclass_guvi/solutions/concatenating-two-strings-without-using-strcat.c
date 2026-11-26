#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    char str1[200] = "";
    char str2[200] = "";
    
    if (scanf("%199s %199s", str1, str2) != 2) {
        return 1;
    }
    
    int len1 = 0;
    while (str1[len1] != '\0') {
        len1++;
    }
    
    int len2 = 0;
    while (str2[len2] != '\0') {
        str1[len1 + len2] = str2[len2];
        len2++;
    }
    
    str1[len1 + len2] = '\0';
    
    printf("%s\n", str1);
    
    return 0;
}
