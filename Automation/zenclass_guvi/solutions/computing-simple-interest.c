#include <stdio.h>
#include <math.h>

int main(void) {
    double P, R, T;
    if (scanf("%lf %lf %lf", &P, &R, &T) != 3) {
        return 0;
    }
    double SI = (P * R * T) / 100.0;
    printf("%.2f\n", SI);
    return 0;
}
