#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int fibonacci(int n) {
    if (n == 0) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    
    if (n <= 0) {
        return 0; // No output for n <= 0
    }
    
    for (int i = 0; i < n; i++) {
        printf("%d", fibonacci(i));
        if (i < n - 1) {
            printf(" ");
        }
    }
    printf("\n");
    
    return 0;
}
