#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int isPalindrome(int n) {
    if (n < 0) return 0;
    int original = n;
    int reverse = 0;
    while (n > 0) {
        reverse = reverse * 10 + n % 10;
        n /= 10;
    }
    return reverse == original;
}

int main(void) {
    int num;
    if (scanf("%d", &num) != 1) return 0;
    if (num == 0) {
        printf("Palindrome\n");
        return 0;
    }
    if (isPalindrome(num)) {
        printf("Palindrome\n");
    } else {
        printf("Not Palindrome\n");
    }
    return 0;
}
