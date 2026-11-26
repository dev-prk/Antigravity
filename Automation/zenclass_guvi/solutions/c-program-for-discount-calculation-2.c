#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    if (n < 0) n = 0;  // handle negative count gracefully
    double *prices = (double *)malloc((size_t)n * sizeof(double));
    for (int i = 0; i < n; ++i) {
        if (scanf("%lf", &prices[i]) != 1) prices[i] = 0.0;
    }
    double discount;
    if (scanf("%lf", &discount) != 1) discount = 0.0;

    double factor = (100.0 - discount) / 100.0;

    printf("Discounted prices:");
    if (n > 0) printf(" ");
    for (int i = 0; i < n; ++i) {
        double discounted = prices[i] * factor;
        printf("%.2f", discounted);
        if (i != n - 1) printf(" ");
    }
    printf("\n");

    free(prices);
    return 0;
}
