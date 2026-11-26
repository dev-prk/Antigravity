#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int savings_balance;
    float current_balance;
    double fixed_deposit_balance;
    
    if (scanf("%d", &savings_balance) != 1) return 0;
    if (scanf("%f", &current_balance) != 1) return 0;
    if (scanf("%lf", &fixed_deposit_balance) != 1) return 0;
    
    double total = (double)savings_balance + (double)current_balance + fixed_deposit_balance;
    
    printf("Total Balance: %.2f\n", total);
    
    return 0;
}
