#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int numCustomers;
    if (scanf("%d", &numCustomers) != 1) {
        return 0;
    }
    
    double totalEarnings = 0.0;
    
    for (int customer = 1; customer <= numCustomers; customer++) {
        int numFruits;
        if (scanf("%d", &numFruits) != 1) {
            return 0;
        }
        
        double customerTotal = 0.0;
        for (int fruit = 1; fruit <= numFruits; fruit++) {
            double price;
            if (scanf("%lf", &price) != 1) {
                return 0;
            }
            customerTotal += price;
        }
        
        printf("Total bill for Customer %d: $%.1f\n", customer, customerTotal);
        totalEarnings += customerTotal;
    }
    
    printf("Total earnings for the day: $%.1f\n", totalEarnings);
    
    return 0;
}
