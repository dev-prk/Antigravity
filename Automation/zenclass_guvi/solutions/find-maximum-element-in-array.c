#include <stdio.h>
#include <limits.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    
    if (n <= 0) {
        printf("0\n");
        return 0;
    }
    
    int max = INT_MIN;
    int val;
    
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &val) != 1) {
            break;
        }
        if (val > max) {
            max = val;
        }
    }
    
    printf("%d\n", max);
    return 0;
}
