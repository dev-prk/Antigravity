#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    
    printf("Debug: Input value is %d\n", n);
    
    if (n % 2 == 0) {
        printf("The number is even\n");
    } else {
        printf("The number is odd\n");
    }
    
    return 0;
}
