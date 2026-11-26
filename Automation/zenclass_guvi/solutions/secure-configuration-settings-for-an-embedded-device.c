#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n < 1 || n > 5) {
        return 1;
    }
    
    double *values = malloc(n * sizeof(double));
    if (values == NULL) {
        return 1;
    }
    
    for (int i = 0; i < n; i++) {
        if (scanf("%lf", &values[i]) != 1) {
            free(values);
            return 1;
        }
    }
    
    const double *const_configs = values;
    
    printf("Configuration Values:\n");
    for (int i = 0; i < n; i++) {
        printf("%.5f\n", const_configs[i]);
    }
    
    free(values);
    return 0;
}
