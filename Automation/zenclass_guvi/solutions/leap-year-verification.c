#include <stdio.h>
int main() {
    int year;
    scanf("%d", &year);
    int is_leap = (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
    if (is_leap) {
        printf("%d is a leap year.", year);
    } else {
        printf("%d is not a leap year.", year);
    }
    return 0;
}
