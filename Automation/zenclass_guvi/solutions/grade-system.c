#include <stdio.h>

int main(void) {
    int marks;
    if (scanf("%d", &marks) != 1) {
        return 0;
    }
    if (marks >= 90) {
        printf("A");
    } else if (marks >= 75) {
        printf("B");
    } else if (marks >= 50) {
        printf("C");
    } else {
        printf("Fail");
    }
    return 0;
}
