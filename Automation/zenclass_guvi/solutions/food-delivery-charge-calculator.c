#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    double d;
    if (scanf("%lf", &d) != 1) {
        return 0;
    }
    double charge;
    if (d <= 3.0) {
        charge = 0.0;
    } else if (d <= 10.0) {
        charge = d * 10.0;
    } else {
        charge = 100.0 + (d - 10.0) * 8.0;
    }
    printf("Delivery Charge: ₹%.2f\n", charge);
    return 0;
}
