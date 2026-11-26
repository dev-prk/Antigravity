#include <stdio.h>
#include <stdlib.h>

int main() {
    int a, b;
    int* pa = &a;
    int* pb = &b;
    
    if (scanf("%d %d", &a, &b) != 2) {
        return 1;
    }
    
    int temp = *pa;
    *pa = *pb;
    *pb = temp;
    
    printf("%d %d\n", a, b);
    
    return 0;
}
