#include <stdio.h>

int totalMinutes(int hours, int minutes) {
    return hours * 60 + minutes;
}

int main(void) {
    int hours, minutes;
    if (scanf("%d %d", &hours, &minutes) != 2) {
        return 0;
    }
    printf("%d\n", totalMinutes(hours, minutes));
    return 0;
}
