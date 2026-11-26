#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int id;
    char *name;
    int qty;
    double price;
} Product;

int find_product(Product *arr, int size, int id) {
    for (int i = 0; i < size; ++i) {
        if (arr[i].id == id) return i;
    }
    return -1;
}

int main(void) {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    getchar(); // consume newline after N

    Product *products = NULL;
    int size = 0, capacity = 0;

    char line[256];
    for (int op = 0; op < N; ++op) {
        if (!fgets(line, sizeof(line), stdin)) break;

        // remove trailing newline
        line[strcspn(line, "\n")] = '\0';

        if (strncmp(line, "ADD", 3) == 0) {
            int id, qty;
            double price;
            char name_buf[128];
            if (sscanf(line, "ADD %d \"%[^\"]\" %d %lf", &id, name_buf, &qty, &price) == 4) {
                if (size == capacity) {
                    int newcap = capacity * 2 + 4;
                    Product *tmp = realloc(products, newcap * sizeof(Product));
                    if (!tmp) return 0; // allocation failed
                    products = tmp;
                    capacity = newcap;
                }
                products[size].id = id;
                products[size].qty = qty;
                products[size].price = price;
                products[size].name = malloc(strlen(name_buf) + 1);
                if (!products[size].name) return 0;
                strcpy(products[size].name, name_buf);
                ++size;
            }
        } else if (strncmp(line, "UPDATE", 6) == 0) {
            int id, qty;
            if (sscanf(line, "UPDATE %d %d", &id, &qty) == 2) {
                int idx = find_product(products, size, id);
                if (idx >= 0) {
                    products[idx].qty = qty;
                    printf("Product updated successfully\n");
                } else {
                    printf("Product not found\n");
                }
            }
        } else if (strncmp(line, "REMOVE", 6) == 0) {
            int id;
            if (sscanf(line, "REMOVE %d", &id) == 1) {
                int idx = find_product(products, size, id);
                if (idx >= 0) {
                    free(products[idx].name);
                    for (int j = idx; j < size - 1; ++j) {
                        products[j] = products[j + 1];
                    }
                    --size;
                    printf("Product removed successfully\n");
                } else {
                    printf("Product not found\n");
                }
            }
        } else if (strncmp(line, "TOTAL", 5) == 0) {
            double total = 0.0;
            for (int i = 0; i < size; ++i) {
                total += products[i].qty * products[i].price;
            }
            printf("%.2f\n", total);
        } else if (strncmp(line, "LIST", 4) == 0) {
            for (int i = 0; i < size; ++i) {
                printf("%d \"%s\" %d %.2f\n",
                       products[i].id,
                       products[i].name,
                       products[i].qty,
                       products[i].price);
            }
        }
    }

    // cleanup
    for (int i = 0; i < size; ++i) free(products[i].name);
    free(products);
    return 0;
}
