#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    for (int i = 0; i < n; i++) {
        int raw, labor, overhead;
        if (scanf("%d %d %d", &raw, &labor, &overhead) != 3) return 0;
        
        long long total_cost = (long long)raw + labor + overhead;
        double gross_profit = total_cost * 0.20;
        double tax_deduction = (gross_profit > 100000) ? gross_profit * 0.15 : gross_profit * 0.10;
        double net_profit = gross_profit - tax_deduction;
        
        char *status;
        if (net_profit >= 75000) {
            status = "Highly Profitable";
        } else if (net_profit >= 50000) {
            status = "Moderately Profitable";
        } else {
            status = "Less Profitable";
        }
        
        printf("Product %d:\n", i + 1);
        printf("Total Production Cost: ₹%lld\n", total_cost);
        printf("Gross Profit: ₹%.2f\n", gross_profit);
        printf("Tax Deduction: ₹%.2f\n", tax_deduction);
        printf("Net Profit: ₹%.2f\n", net_profit);
        printf("Product Status: %s\n", status);
    }
    
    return 0;
}
