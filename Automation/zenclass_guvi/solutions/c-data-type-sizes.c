#include <stdio.h>
#include <string.h>

int main() {
    char dtype[20];
    scanf("%s", dtype);
    
    if (strcmp(dtype, "int") == 0) {
        printf("%zu\n", sizeof(int));
    } else if (strcmp(dtype, "float") == 0) {
        printf("%zu\n", sizeof(float));
    } else if (strcmp(dtype, "double") == 0) {
        printf("%zu\n", sizeof(double));
    } else if (strcmp(dtype, "char") == 0) {
        printf("%zu\n", sizeof(char));
    }
    
    return 0;
}
