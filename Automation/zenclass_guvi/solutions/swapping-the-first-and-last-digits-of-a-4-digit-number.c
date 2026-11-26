#include <stdio.h>
int main(void) {
    int num;
    scanf("%d", &num);
    
    int first = num / 1000;
    int last = num % 10;
    int middle = (num / 10) % 100;
    
    int result = last * 1000 + middle * 10 + first;
    printf("%d\n", result);
    
    return 0;
}
