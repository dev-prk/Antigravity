#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    double P, R, T;
    if (scanf("%lf", &P) != 1) return 0;
    if (scanf("%lf", &R) != 1) return 0;
    if (scanf("%lf", &T) != 1) return 0;
    
    double SI = (P * R * T) / 100.0;
    
    // Round to nearest integer
    long long rounded = (long long)(SI + 0.5);
    
    // Check if SI is already an integer (within floating point precision)
    double diff = fabs(SI - rounded);
    if (diff < 1e-9) {
        // SI is effectively an integer
        printf("%lld\n", rounded);
    } else {
        // Output with sufficient precision
        printf("%.10g\n", SI);
    }
    
    return 0;
}
