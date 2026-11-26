#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

float calculateBaseBonus(float performanceScore) {
    return performanceScore * 50.0f;
}

float calculateAdditionalBonus(float workHours) {
    return workHours * 10.0f;
}

float applyAdjustment(float bonus, char employeeType) {
    if (employeeType == 'P') {
        return bonus * 0.95f;
    }
    return bonus;
}

int main() {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    for (int i = 0; i < N; i++) {
        float perf, hours;
        char type;
        
        if (scanf("%f %f %c", &perf, &hours, &type) != 3) {
            if (i == 0) continue;
            break;
        }
        
        float base = calculateBaseBonus(perf);
        float additional = calculateAdditionalBonus(hours);
        float total = base + additional;
        float final = applyAdjustment(total, type);
        
        printf("%.2f\n", final);
    }
    
    return 0;
}
