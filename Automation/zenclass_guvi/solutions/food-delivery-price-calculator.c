#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

double calculateTotalCost(float prices[], int quantities[], int n) {
    double total = 0.0;
    for (int i = 0; i < n; i++) {
        total += prices[i] * quantities[i];
    }
    return total;
}

double applyDiscount(double totalCost) {
    if (totalCost < 50.0) {
        return 0.0;
    } else if (totalCost <= 100.0) {
        return totalCost * 0.10;
    } else {
        return totalCost * 0.20;
    }
}

double finalPriceAfterDiscount(double totalCost) {
    double discount = applyDiscount(totalCost);
    return totalCost - discount;
}

int main() {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    for (int order = 0; order < N; order++) {
        int M;
        if (scanf("%d", &M) != 1) break;
        
        if (M <= 0) {
            printf("0.00\n");
            continue;
        }
        
        float *prices = (float *)malloc(M * sizeof(float));
        int *quantities = (int *)malloc(M * sizeof(int));
        
        if (prices == NULL || quantities == NULL) {
            free(prices);
            free(quantities);
            printf("0.00\n");
            continue;
        }
        
        int count = 0;
        while (count < M) {
            if (scanf("%f", &prices[count]) != 1) break;
            if (scanf("%d", &quantities[count]) != 1) break;
            count++;
        }
        
        double total = calculateTotalCost(prices, quantities, count);
        double final = finalPriceAfterDiscount(total);
        
        printf("%.2f\n", final);
        
        free(prices);
        free(quantities);
    }
    
    return 0;
}
