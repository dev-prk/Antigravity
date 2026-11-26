#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int n1;
    if (scanf("%d", &n1) != 1) return 0;
    
    int *arr1 = malloc(n1 * sizeof(int));
    for (int i = 0; i < n1; i++) {
        scanf("%d", &arr1[i]);
    }
    
    int n2;
    scanf("%d", &n2);
    
    int *arr2 = malloc(n2 * sizeof(int));
    for (int i = 0; i < n2; i++) {
        scanf("%d", &arr2[i]);
    }
    
    int equal = 1;
    if (n1 != n2) {
        equal = 0;
    } else {
        for (int i = 0; i < n1; i++) {
            if (arr1[i] != arr2[i]) {
                equal = 0;
                break;
            }
        }
    }
    
    if (equal) {
        printf("Arrays are equal.\n");
    } else {
        printf("Arrays are not equal.\n");
    }
    
    free(arr1);
    free(arr2);
    return 0;
}
