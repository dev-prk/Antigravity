#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int i;
    float f;
    char c;
    scanf("%d %f %c", &i, &f, &c);
    printf("%d\n", i);
    printf("%.2f\n", f);
    printf("%c\n", c);
    return 0;
}
