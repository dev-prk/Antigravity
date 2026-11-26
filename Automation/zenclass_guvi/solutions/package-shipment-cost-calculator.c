#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

const char* get_weight_category(float weight) {
    if (weight <= 0) return "Invalid";
    if (weight <= 5) return "Lightweight";
    if (weight <= 20) return "Standard";
    if (weight <= 50) return "Heavy";
    return "Overweight";
}

double get_rate(const char* category, const char* type) {
    int is_domestic = (strcmp(type, "domestic") == 0);
    
    if (strcmp(category, "Lightweight") == 0) {
        return is_domestic ? 1.0 : 2.0;
    } else if (strcmp(category, "Standard") == 0) {
        return is_domestic ? 1.5 : 3.0;
    } else if (strcmp(category, "Heavy") == 0) {
        return is_domestic ? 2.0 : 4.0;
    } else if (strcmp(category, "Overweight") == 0) {
        return is_domestic ? 3.0 : 6.0;
    }
    return 0.0;
}

int main() {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    for (int i = 0; i < N; i++) {
        float weight;
        int distance;
        char type[20];
        
        if (scanf("%f %d %19s", &weight, &distance, type) != 3) {
            fprintf(stderr, "-1\n");
            return 1;
        }
        
        const char* category = get_weight_category(weight);
        if (strcmp(category, "Invalid") == 0) {
            fprintf(stderr, "-1\n");
            return 1;
        }
        
        double rate = get_rate(category, type);
        double cost = (double)distance * rate;
        
        printf("%s\n", category);
        printf("%s\n", type);
        printf("%.2f\n", cost);
    }
    
    return 0;
}
