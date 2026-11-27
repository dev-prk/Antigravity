#include <stdio.h>
int main(void) {
    int num;
    scanf("%d", &num);
    int i;
    for (i = 2; i < num; i++) {
        if (num % i == 0) {
            printf("Not Prime");
            return 0;
        }
    }
    printf("Prime");
    return 0;
}
