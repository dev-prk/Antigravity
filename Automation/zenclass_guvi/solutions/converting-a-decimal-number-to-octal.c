#include <stdio.h>
int main(void) {
    int num;
    scanf("%d", &num);
    
    int digit1 = num / 64;
    int digit2 = (num / 8) % 8;
    int digit3 = num % 8;
    
    printf("%d%d%d\n", digit1, digit2, digit3);
    return 0;
}
