#include <stdio.h>

int main() {
    int N;
    scanf("%d", &N);
    
    for (int i = N; i >= 1; i--) {
        // Print leading spaces for alignment
        for (int s = 0; s < N - i; s++) {
            printf(" ");
        }
        
        // Print numbers from i down to 1
        for (int j = i; j >= 1; j--) {
            if (j < i) {
                printf(" ");
            }
            printf("%d", j);
        }
        
        printf(" \n");
    }
    
    return 0;
}
