#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <math.h>

long long aggregator(const char *op, int n, ...) {
    if (n <= 0) {
        return -1;
    }
    
    va_list args;
    va_start(args, n);
    
    if (strcmp(op, "sum") == 0) {
        long long sum = 0;
        for (int i = 0; i < n; i++) {
            sum += va_arg(args, int);
        }
        va_end(args);
        return sum;
    }
    else if (strcmp(op, "product") == 0) {
        long long prod = 1;
        for (int i = 0; i < n; i++) {
            prod *= va_arg(args, int);
        }
        va_end(args);
        return prod;
    }
    else if (strcmp(op, "max") == 0) {
        int max_val = va_arg(args, int);
        for (int i = 1; i < n; i++) {
            int val = va_arg(args, int);
            if (val > max_val) {
                max_val = val;
            }
        }
        va_end(args);
        return max_val;
    }
    
    va_end(args);
    return -1;
}

int main() {
    char op[20];
    int n;
    
    if (scanf("%19s", op) != 1) {
        printf("-1\n");
        return 0;
    }
    
    if (scanf("%d", &n) != 1 || n <= 0 || n > 100) {
        printf("-1\n");
        return 0;
    }
    
    int *values = malloc(n * sizeof(int));
    if (values == NULL) {
        printf("-1\n");
        return 0;
    }
    
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &values[i]) != 1) {
            free(values);
            printf("-1\n");
            return 0;
        }
    }
    
    long long result;
    
    if (strcmp(op, "sum") == 0) {
        result = 0;
        for (int i = 0; i < n; i++) {
            result += values[i];
        }
    }
    else if (strcmp(op, "product") == 0) {
        result = 1;
        for (int i = 0; i < n; i++) {
            result *= values[i];
        }
    }
    else if (strcmp(op, "max") == 0) {
        result = values[0];
        for (int i = 1; i < n; i++) {
            if (values[i] > result) {
                result = values[i];
            }
        }
    }
    else {
        free(values);
        printf("-1\n");
        return 0;
    }
    
    free(values);
    printf("%lld\n", result);
    
    return 0;
}
