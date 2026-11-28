#include <stdio.h>
#include <limits.h>

int main(void) {
    long long n;
    if (scanf("%lld", &n) != 1) return 0;

    // Check signed types
    int fits_short = (n >= SHRT_MIN && n <= SHRT_MAX);
    int fits_long = (n >= LONG_MIN && n <= LONG_MAX);
    
    // Check unsigned types
    int fits_ushort = (n >= 0 && n <= (unsigned short)USHRT_MAX);
    int fits_ulong = (n >= 0 && n <= (unsigned long)ULONG_MAX);

    // Print signed types
    if (fits_short) {
        printf("Fits in short int\n");
    }
    if (fits_long) {
        printf("Fits in long int\n");
    }

    // Print unsigned types
    int any_unsigned = 0;
    if (fits_ushort) {
        printf("Fits in unsigned short int\n");
        any_unsigned = 1;
    }
    if (fits_ulong) {
        printf("Fits in unsigned long int\n");
        any_unsigned = 1;
    }
    
    // If no unsigned type fits, print the message
    if (!any_unsigned) {
        printf("Does not fit in any type\n");
    }

    return 0;
}
