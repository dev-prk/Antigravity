#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    double amount;
    if (scanf("%lf", &amount) != 1) {
        return 1;
    }
    
    double discount = 0.0;
    
    if (amount >= 1000.0 && amount <= 5000.0) {
        discount = amount * 0.10;
    } else if (amount > 5000.0) {
        discount = amount * 0.20;
    }
    
    double final_amount = amount - discount;
    
    printf("Original Amount: %.2f\n", amount);
    printf("Discount: %.2f\n", discount);
    printf("Final Amount: %.2f\n", final_amount);
    
    return 0;
}
