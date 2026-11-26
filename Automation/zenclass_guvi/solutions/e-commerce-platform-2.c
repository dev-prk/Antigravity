#include <stdio.h>
#include <stdlib.h>

float calculateTotalCost(int items[], int n) {
    if (n <= 0) 
        return 0;
    return items[n-1] + calculateTotalCost(items, n-1);
}

float applyDiscount(float totalCost, int itemCount) {
    float discount = 0;
    if (itemCount > 10) {
        discount = 0.15;
    } else if (itemCount >= 6) {
        discount = 0.10;
    } else if (itemCount >= 1) {
        discount = 0.05;
    }
    return totalCost * (1 - discount);
}

int main() {
    int n;
    scanf("%d", &n);
    int items[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &items[i]);
    }
    float total = calculateTotalCost(items, n);
    float finalCost = applyDiscount(total, n);
    printf("%.2f\n", finalCost);
    return 0;
}
