#include <stdio.h>
int main(void) {
    int n;
    scanf("%d", &n);
    
    if (n == 0) {
        printf("0");
        return 0;
    }
    
    int bits[10];
    int i = 0;
    
    while (n > 0) {
        bits[i] = n % 2;
        n = n / 2;
        i++;
    }
    
    for (int j = i - 1; j >= 0; j--) {
        printf("%d", bits[j]);
    }
    
    return 0;
}
