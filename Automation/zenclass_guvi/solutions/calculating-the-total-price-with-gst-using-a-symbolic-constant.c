#include <stdio.h>

#define GST_RATE 18

int main(void) {
    double price;
    if (scanf("%lf", &price) != 1) {
        return 1;
    }
    double total = price + price * GST_RATE / 100.0;
    printf("%.2f\n", total);
    return 0;
}
