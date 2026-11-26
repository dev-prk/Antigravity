#include <stdio.h>
int main(void) {
    int num;
    scanf("%d", &num);
    
    int last_digit = num % 10;
    int middle_digit = (num / 10) % 10;
    int first_digit = num / 100;
    
    int sum = first_digit + middle_digit + last_digit;
    printf("%d\n", sum);
    
    return 0;
}
