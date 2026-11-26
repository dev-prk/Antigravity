#include <stdio.h>

int main(void) {
    int age;
    if (scanf("%d", &age) != 1) return 0;
    int price;
    if (age <= 12) {
        price = 50;
    } else if (age <= 59) {
        price = 100;
    } else {
        price = 70;
    }
    printf("%d", price);
    return 0;
}
