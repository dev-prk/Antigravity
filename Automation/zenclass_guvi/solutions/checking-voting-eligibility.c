#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int age;
    if (scanf("%d", &age) != 1) {
        return 1;
    }
    if (age >= 18) {
        printf("Eligible\n");
    } else {
        printf("Not Eligible\n");
    }
    return 0;
}
