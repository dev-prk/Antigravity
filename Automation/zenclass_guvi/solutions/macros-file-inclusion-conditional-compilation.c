#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int experience;
    if (scanf("%d", &experience) != 1) {
        return 1;
    }
    
    if (experience < 5) {
        printf("Junior\nSalary: 30000\n");
    } else if (experience <= 10) {
        printf("Mid-level\nSalary: 50000\n");
    } else {
        printf("Senior\nSalary: 70000\n");
    }
    
    return 0;
}
