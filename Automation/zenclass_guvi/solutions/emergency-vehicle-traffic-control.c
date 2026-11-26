#include <stdio.h>

int main() {
    char T;
    int E;
    
    scanf(" %c", &T);
    scanf("%d", &E);
    
    if (T == 'R') {
        if (E == 1) {
            printf("ALLOW EMERGENCY");
        } else {
            printf("STOP");
        }
    } else if (T == 'Y') {
        if (E == 1) {
            printf("ALLOW EMERGENCY");
        } else {
            printf("PREPARE TO STOP");
        }
    } else if (T == 'G') {
        if (E == 1) {
            printf("CLEAR THE WAY");
        } else {
            printf("PROCEED");
        }
    }
    
    return 0;
}
