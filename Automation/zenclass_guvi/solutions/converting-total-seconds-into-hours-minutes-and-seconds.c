#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int totalSeconds;
    if (scanf("%d", &totalSeconds) != 1) {
        return 1;
    }
    
    int hours = totalSeconds / 3600;
    int remaining = totalSeconds % 3600;
    int minutes = remaining / 60;
    int seconds = remaining % 60;
    
    printf("%d\n%d\n%d\n", hours, minutes, seconds);
    
    return 0;
}
