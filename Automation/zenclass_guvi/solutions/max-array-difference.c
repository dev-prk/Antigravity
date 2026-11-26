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
    int val;
    
    for (int i = 0; i < N; i++) {
        if (scanf("%d", &val) == 1) {
            if (first) {
                min_val = val;
                max_val = val;
                first = 0;
            } else {
                if (val < min_val) min_val = val;
                if (val > max_val) max_val = val;
            }
        }
    }
    
    printf("%d\n", max_val - min_val);
    return 0;
}
