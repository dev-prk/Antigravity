#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    for (int i = 0; i < n; i++) {
        int a;
        double b, c;
        char op;
        
        if (scanf("%d %lf %c %lf", &a, &b, &op, &c) != 4) break;
        
        double result;
        switch (op) {
            case '+': result = a + b + c; break;
            case '-': result = a - b + c; break;
            case '*': result = a * b + c; break;
            case '/': 
                if (b == 0.0) result = c;
                else result = a / b + c;
                break;
            default: result = c; break;
        }
        
        printf("%.2f\n", result);
    }
    
    return 0;
}
