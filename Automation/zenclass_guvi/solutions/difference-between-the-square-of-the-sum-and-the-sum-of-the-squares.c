#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    long long a, b, c;
    if (scanf("%lld%lld%lld", &a, &b, &c) != 3) {
        return 1;
    }
    
    long long sum_of_squares = a * a + b * b + c * c;
    long long sum = a + b + c;
    long long square_of_sum = sum * sum;
    long long difference = square_of_sum - sum_of_squares;
    
    printf("%lld\n", sum_of_squares);
    printf("%lld\n", square_of_sum);
    printf("%lld\n", difference);
    
    return 0;
}
