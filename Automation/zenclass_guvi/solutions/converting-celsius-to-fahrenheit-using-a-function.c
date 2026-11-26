#include <stdio.h>

float celsiusToFahrenheit(float celsius) {
    return celsius * 9.0f / 5.0f + 32.0f;
}

int main(void) {
    float celsius;
    if (scanf("%f", &celsius) != 1) {
        return 0;
    }
    float fahrenheit = celsiusToFahrenheit(celsius);
    printf("%.2f\n", fahrenheit);
    return 0;
}
