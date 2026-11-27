#include <stdio.h>
#define PI 3.14

float circleArea(float r) {
    return PI * r * r;
}

float squareArea(float side) {
    return side * side;
}

float triangleArea(float base, float height) {
    return 0.5 * base * height;
}

int main(void) {
    int choice;
    float area;
    
    scanf("%d", &choice);
    
    switch (choice) {
        case 1: {
            float radius;
            scanf("%f", &radius);
            area = circleArea(radius);
            break;
        }
        case 2: {
            float side;
            scanf("%f", &side);
            area = squareArea(side);
            break;
        }
        case 3: {
            float base, height;
            scanf("%f %f", &base, &height);
            area = triangleArea(base, height);
            break;
        }
    }
    
    printf("%.2f\n", area);
    
    return 0;
}
