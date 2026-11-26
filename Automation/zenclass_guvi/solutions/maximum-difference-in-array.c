#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    if (N <= 0) {
        printf("0\n");
        return 0;
    }
    
    int min_val = 0, max_val = 0;
    int first = 1;
    
    for (int i = 0; i < N; i++) {
        int x;
        if (scanf("%d", &x) != 1) return 0;
        
        if (first) {
            min_val = x;
            max_val = x;
            first = 0;
        } else {
            if (x < min_val) min_val = x;
            if (x > max_val) max_val = x;
        }
    }
    
    printf("%d\n", max_val - min_val);
    return 0;
}
