#include <stdio.h>

int main() {
    int temp;
    scanf("%d", &temp);
    
    if (temp < 0) {
        printf("Freezing\n");
    } else if (temp <= 20) {
        printf("Cold\n");
    } else if (temp <= 30) {
        printf("Moderate\n");
    } else {
        printf("Hot\n");
    }
    
    return 0;
}
