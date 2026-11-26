#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int n;
    if (scanf("%d", &n) != 1) {
        return 0;
    }
    
    long sum = 0;
    for (int i = 0; i < n; i++) {
        int x;
        if (scanf("%d", &x) != 1) {
            break;
        }
        sum += x;
    }
    
    float avg = (float)sum / (float)n;
    printf("%.2f\n", avg);
    
    return 0;
}
