#include <stdio.h>
#include <limits.h>

int main() {
    int n;
    scanf("%d", &n);
    
    int largest = INT_MIN;
    int second_largest = INT_MIN;
    
    for (int i = 0; i < n; i++) {
        int num;
        scanf("%d", &num);
        
        if (num > largest) {
            second_largest = largest;
            largest = num;
        } else if (num > second_largest && num < largest) {
            second_largest = num;
        }
    }
    
    printf("%d\n", second_largest);
    
    return 0;
}
