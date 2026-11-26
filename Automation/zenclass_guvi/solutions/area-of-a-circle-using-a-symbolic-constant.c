#include <stdio.h>
#define PI 3.14

int main(void) {
    float radius;
    scanf("%f", &radius);
    float area = PI * radius * radius;
    printf("%.2f\n", area);
    return 0;
}
