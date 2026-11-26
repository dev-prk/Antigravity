#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int N;
    if (scanf("%d", &N) != 1) {
        return 1;
    }
    
    int sum = 0;
    int counter = 1;
    while (counter <= N) {
        sum += counter;
        counter++;
    }
    
    printf("%d\n", sum);
    return 0;
}
