#include <stdio.h>

int basePrice = 50;

int main(void) {
    int quantity;
    scanf("%d", &quantity);
    int totalCost = basePrice * quantity;
    printf("%d\n%d\n", basePrice, totalCost);
    return 0;
}
