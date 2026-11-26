#include <stdio.h>
int main(void) {
    int num;
    scanf("%d", &num);
    
    int last_digit = num % 10;
    int middle_digit = (num / 10) % 10;
    int first_digit = num / 100;
    
    int reversed = last_digit * 100 + middle_digit * 10 + first_digit;
    printf("%d\n", reversed);
    
    return 0;
}
