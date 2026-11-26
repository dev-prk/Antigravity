#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char op[20], type[20];
    scanf("%s %s", op, type);
    int n;
    scanf("%d", &n);
    long long sum = 0;
    long long maxVal = 0;
    int first = 1;
    for (int i = 0; i < n; i++) {
        long long v;
        scanf("%lld", &v);
        sum += v;
        if (first || v > maxVal) {
            maxVal = v;
            first = 0;
        }
    }
    if (strcmp(op, "sum") == 0) {
        printf("%lld\n", sum);
    } else if (strcmp(op, "max") == 0) {
        printf("%lld\n", maxVal);
    } else if (strcmp(op, "average") == 0) {
        double avg = (double)sum / n;
        printf("%.10f\n", avg);
    }
    return 0;
}
