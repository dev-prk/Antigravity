#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int rectangleArea(int length, int breadth) {
    return length * breadth;
}

int main(void) {
    int length, breadth;
    if (scanf("%d %d", &length, &breadth) != 2) {
        return -1;
    }
    int area = rectangleArea(length, breadth);
    printf("%d\n", area);
    return 0;
}
