#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int isLeapYear(int year) {
    if (year % 400 == 0) {
        return 1;
    }
    if (year % 100 == 0) {
        return 0;
    }
    if (year % 4 == 0) {
        return 1;
    }
    return 0;
}

int daysInMonth(int month, int year) {
    int days;
    switch (month) {
        case 1:
        case 3:
        case 5:
        case 7:
        case 8:
        case 10:
        case 12:
            days = 31;
            break;
        case 4:
        case 6:
        case 9:
        case 11:
            days = 30;
            break;
        case 2:
            if (isLeapYear(year)) {
                days = 29;
            } else {
                days = 28;
            }
            break;
        default:
            days = 0;
            break;
    }
    return days;
}

int main(void) {
    int month, year;
    if (scanf("%d %d", &month, &year) != 2) {
        return 1;
    }
    printf("%d\n", daysInMonth(month, year));
    return 0;
}
