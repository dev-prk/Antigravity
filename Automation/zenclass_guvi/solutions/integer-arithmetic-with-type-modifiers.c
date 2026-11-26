#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    short a;
    long long b;
    
    if (scanf("%hd %lld", &a, &b) != 2) {
        return 1;
    }
    
    long long sum = (long long)a + b;
    long long diff = b - a;
    long long prod = (long long)a * b;
    
    if (a == 0) {
        printf("Division by zero is not allowed.\n");
    } else {
        long long div = b / a;
        printf("Sum: %lld\n", sum);
        printf("Difference: %lld\n", diff);
        printf("Product: %lld\n", prod);
        printf("Division: %lld\n", div);
    }
    
    return 0;
}
