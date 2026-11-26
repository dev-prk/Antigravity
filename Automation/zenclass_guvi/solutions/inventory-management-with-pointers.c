#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NAME_LEN 100

typedef struct {
    char name[MAX_NAME_LEN];
    char supplier_name[MAX_NAME_LEN];
    float price;
} Supplier;

typedef struct {
    char name[MAX_NAME_LEN];
    int num_suppliers;
    Supplier *suppliers;
} Product;

void find_cheapest_supplier(Product *product, char *cheapest_name) {
    if (product->num_suppliers == 0) {
        strcpy(cheapest_name, "");
        return;
    }
    
    float min_price = product->suppliers[0].price;
    strcpy(cheapest_name, product->suppliers[0].supplier_name);
    
    for (int i = 1; i < product->num_suppliers; i++) {
        if (product->suppliers[i].price < min_price) {
            min_price = product->suppliers[i].price;
            strcpy(cheapest_name, product->suppliers[i].supplier_name);
        }
    }
}

float calculate_average_price(Product *product) {
    if (product->num_suppliers == 0) {
        return 0.0f;
    }
    
    float sum = 0.0f;
    for (int i = 0; i < product->num_suppliers; i++) {
        sum += product->suppliers[i].price;
    }
    
    return sum / product->num_suppliers;
}

int main() {
    int num_products;
    scanf("%d", &num_products);
    
    Product *products = (Product *)malloc(num_products * sizeof(Product));
    
    for (int i = 0; i < num_products; i++) {
        scanf("%s", products[i].name);
        
        scanf("%d", &products[i].num_suppliers);
        
        products[i].suppliers = (Supplier *)malloc(products[i].num_suppliers * sizeof(Supplier));
        
        for (int j = 0; j < products[i].num_suppliers; j++) {
            scanf("%s %f", products[i].suppliers[j].supplier_name, &products[i].suppliers[j].price);
        }
    }
    
    for (int i = 0; i < num_products; i++) {
        char cheapest_name[MAX_NAME_LEN];
        find_cheapest_supplier(&products[i], cheapest_name);
        float avg_price = calculate_average_price(&products[i]);
        
        printf("Product: %s\n", products[i].name);
        printf("Average Price: %.2f\n", avg_price);
        printf("Cheapest Supplier: %s\n", cheapest_name);
    }
    
    for (int i = 0; i < num_products; i++) {
        free(products[i].suppliers);
    }
    free(products);
    
    return 0;
}
