#include <stdio.h>
int main(void) {
    int a, b;
    char op;
    scanf("%d %d %c", &a, &b, &op);
    int result;
    switch (op) {
        case '+': result = a + b; break;
        case '-': result = a - b; break;
        case '*': result = a * b; break;
        case '/': result = a / b; break;
    }
    printf("%d\n", result);
    return 0;
}
