#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

void printMessage(int times) {
    for (int i = 0; i < times; i++) {
        printf("Learning C is fun\n");
    }
}

int main(void) {
    int N;
    if (scanf("%d", &N) != 1) {
        return 1;
    }
    printMessage(N);
    return 0;
}
