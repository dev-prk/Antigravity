#include <stdio.h>

int isPerfect(int num) {
    if (num <= 1) {
        return 0;
    }
    int sum = 0;
    for (int i = 1; i < num; i++) {
        if (num % i == 0) {
            sum += i;
        }
    }
    return sum == num ? 1 : 0;
}

int main(void) {
    int num;
    if (scanf("%d", &num) != 1) {
        return 1;
    }
    if (isPerfect(num)) {
        printf("Perfect\n");
    } else {
        printf("Not Perfect\n");
    }
    return 0;
}
