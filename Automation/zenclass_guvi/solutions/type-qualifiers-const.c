#include <stdio.h>

int main() {
    int n;
    scanf("%d", &n);
    
    float temp_readings[10];
    
    for (int i = 0; i < n; i++) {
        scanf("%f", &temp_readings[i]);
    }
    
    printf("Sensor Readings:\n");
    for (int i = 0; i < n; i++) {
        printf("%.2f\n", temp_readings[i]);
    }
    
    return 0;
}
