#include <stdio.h>
void printDigits(int n) {
    if (n > 0) {
        printDigits(n / 10);
        printf("%d\n", n % 10);
    }
}
int main(void) {
    int num;
    scanf("%d", &num);
    printDigits(num);
    return 0;
}
