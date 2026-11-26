#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int S, C;
    if (scanf("%d", &S) != 1) return 0;
    scanf("%d", &C);
    
    int *inventory = (int *)malloc(S * C * sizeof(int));
    if (inventory == NULL) return 1;
    
    for (int i = 0; i < S * C; i++) {
        scanf("%d", &inventory[i]);
    }
    
    int X;
    scanf("%d", &X);
    
    int *ptr = inventory;
    for (int i = 0; i < S * C; i++) {
        *ptr += X;
        ptr++;
    }
    
    ptr = inventory;
    for (int sec = 0; sec < S; sec++) {
        for (int cat = 0; cat < C; cat++) {
            printf("%d", *ptr);
            ptr++;
            if (cat < C - 1) {
                printf(" ");
            }
        }
        if (sec < S - 1) {
            printf("\n");
        }
    }
    
    free(inventory);
    return 0;
}
