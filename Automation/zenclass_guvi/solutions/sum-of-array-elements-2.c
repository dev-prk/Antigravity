#include <stdio.h>
#include <stdlib.h>

int main() {
    int N;
    scanf("%d", &N);
    
    long long sum = 0;
    for (int i = 0; i < N; i++) {
        int num;
        scanf("%d", &num);
        sum += num;
    }
    
    printf("%lld\n", sum);
    return 0;
}
