#include <stdio.h>
int main(void) {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    int arr[N];
    for (int i = 0; i < N; i++) {
        scanf("%d", &arr[i]);
    }
    
    for (int i = 0; i < N; i++) {
        printf("%d", arr[i]);
        if (i < N - 1) {
            printf(" ");
        }
    }
    printf("\n");
    
    return 0;
}
