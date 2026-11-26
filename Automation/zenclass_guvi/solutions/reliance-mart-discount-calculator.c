#include <stdio.h>

int main() {
    double amount, discount, final_price;
    
    scanf("%lf", &amount);
    
    if (amount >= 1000) {
        discount = amount * 0.20;
        final_price = amount - discount;
    } else if (amount >= 500) {
        discount = amount * 0.10;
        final_price = amount - discount;
    } else {
        discount = 0;
        final_price = amount;
    }
    
    printf("Discount: %.2lf, Final Price: %.2lf\n", discount, final_price);
    
    return 0;
}
