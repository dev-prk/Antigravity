#include <stdio.h>
#include <stdlib.h>

float calculateTotalCost(int items[], int n) {
    if (n <= 0) {
        return 0.0;
    }
    if (n == 1) {
        return (float)items[0];
    }
    return (float)items[0] + calculateTotalCost(items + 1, n - 1);
}

float applyDiscount(float totalCost, int itemCount) {
    float discountPercent = 0.0;
    
    if (itemCount >= 1 && itemCount <= 5) {
        discountPercent = 5.0;
    } else if (itemCount >= 6 && itemCount <= 10) {
        discountPercent = 10.0;
    } else if (itemCount > 10) {
        discountPercent = 15.0;
    }
    
    float discountAmount = totalCost * (discountPercent / 100.0);
    float finalCost = totalCost - discountAmount;
    
    return finalCost;
}

int main() {
    int n;
    scanf("%d", &n);
    
    if (n <= 0) {
        printf("0.00\n");
        return 0;
    }
    
    int *items = (int *)malloc(n * sizeof(int));
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &items[i]);
    }
    
    float totalCost = calculateTotalCost(items, n);
    float finalCost = applyDiscount(totalCost, n);
    
    printf("%.2f\n", finalCost);
    
    free(items);
    
    return 0;
}
