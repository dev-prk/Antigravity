#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int age;
    if (scanf("%d", &age) == 1) {
        if (age >= 18) {
            printf("You are eligible to vote.");
        } else {
            printf("You are not eligible to vote.");
        }
    }
    return 0;
}
