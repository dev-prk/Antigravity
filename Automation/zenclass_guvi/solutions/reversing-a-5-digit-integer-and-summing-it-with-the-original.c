#include <stdio.h>
int main(void) {
    int num, original, digits[5], reversed = 0, sum;
    
    scanf("%d", &num);
    original = num;
    
    digits[0] = num % 10; num /= 10;
    digits[1] = num % 10; num /= 10;
    digits[2] = num % 10; num /= 10;
    digits[3] = num % 10; num /= 10;
    digits[4] = num % 10;
    
    reversed = digits[0] * 10000 + digits[1] * 1000 + digits[2] * 100 + digits[3] * 10 + digits[4];
    sum = original + reversed;
    
    printf("%d\n%d\n", reversed, sum);
    
    return 0;
}
