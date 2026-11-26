#include <stdio.h>

int main(void) {
    int a, b;
    char op;

    if (scanf("%d %d %c", &a, &b, &op) != 3) {
        return 1;
    }

    int result;
    switch (op) {
        case '+':
            result = a + b;
            break;
        case '-':
            result = a - b;
            break;
        case '*':
            result = a * b;
            break;
        case '/':
            if (b != 0) {
                result = a / b;
            } else {
                result = 0;
            }
            break;
        default:
            return 1;
    }

    printf("%d\n", result);
    return 0;
}
