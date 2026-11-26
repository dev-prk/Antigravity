#include <stdio.h>

int main(void) {
    enum Day { Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday };

    int dayNumber = 0;
    if (scanf("%d", &dayNumber) != 1) {
        return 0;
    }

    enum Day d = (enum Day)dayNumber;
    printf("%d\n", (int)d);

    return 0;
}
