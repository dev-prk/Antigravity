#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int m1, m2, m3;
    if (scanf("%d %d %d", &m1, &m2, &m3) != 3) {
        return 1;
    }
    int total = m1 + m2 + m3;
    double percentage = total * 100.0 / 300.0;
    printf("%d\n", total);
    printf("%.2f\n", percentage);
    return 0;
}
