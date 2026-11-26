#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_NAME_LEN 100
#define MAX_SUPPLIERS 100

typedef struct {
    char name[MAX_NAME_LEN];
    int price_count;
    char cheapest_supplier[MAX_NAME_LEN];
    double total_price;
    double min_price;
} Product;

int main() {
    int p;
    if (scanf("%d", &p) != 1) return 0;
    
    Product *products = malloc(p * sizeof(Product));
    if (!products) return 0;
    
    for (int i = 0; i < p; i++) {
        products[i].total_price = 0.0;
        products[i].min_price = 1e18;
        products[i].price_count = 0;
        products[i].cheapest_supplier[0] = '\0';
        
        char temp[MAX_NAME_LEN];
        if (scanf("%99s", temp) == 1) {
            strncpy(products[i].name, temp, MAX_NAME_LEN - 1);
            products[i].name[MAX_NAME_LEN - 1] = '\0';
        }
        
        int s;
        if (scanf("%d", &s) != 1) s = 0;
        products[i].price_count = s;
        
        for (int j = 0; j < s; j++) {
            char supplier_name[MAX_NAME_LEN];
            double price;
            if (scanf("%99s %lf", supplier_name, &price) == 2) {
                products[i].total_price += price;
                if (price < products[i].min_price) {
                    products[i].min_price = price;
                    strncpy(products[i].cheapest_supplier, supplier_name, MAX_NAME_LEN - 1);
                    products[i].cheapest_supplier[MAX_NAME_LEN - 1] = '\0';
                }
            }
        }
    }
    
    for (int i = 0; i < p; i++) {
        double avg = 0.0;
        if (products[i].price_count > 0) {
            avg = products[i].total_price / products[i].price_count;
        }
        
        printf("Product: %s\n", products[i].name);
        printf("Average Price: %.2f\n", avg);
        printf("Cheapest Supplier: %s\n", products[i].cheapest_supplier);
    }
    
    free(products);
    return 0;
}
