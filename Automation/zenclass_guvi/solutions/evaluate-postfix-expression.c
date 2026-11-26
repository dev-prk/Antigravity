#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int stack[1000];
int top = -1;

void push(int x) {
    stack[++top] = x;
}

int pop() {
    return stack[top--];
}

int evaluatePostfix(char* exp) {
    int len = strlen(exp);
    int i = 0;
    
    while (i < len) {
        // Skip whitespace
        while (i < len && exp[i] == ' ') {
            i++;
        }
        
        if (i >= len) break;
        
        // Check if it's a number
        if (isdigit(exp[i]) || (exp[i] == '-' && isdigit(exp[i+1]))) {
            int num = 0;
            int sign = 1;
            
            if (exp[i] == '-') {
                sign = -1;
                i++;
            }
            
            while (i < len && isdigit(exp[i])) {
                num = num * 10 + (exp[i] - '0');
                i++;
            }
            
            push(sign * num);
        } else {
            // It's an operator
            int val1 = pop();
            int val2 = pop();
            
            switch (exp[i]) {
                case '+':
                    push(val2 + val1);
                    break;
                case '-':
                    push(val2 - val1);
                    break;
                case '*':
                    push(val2 * val1);
                    break;
                case '/':
                    push(val2 / val1);
                    break;
            }
            i++;
        }
    }
    
    return pop();
}

int main() {
    char exp[10000];
    
    if (fgets(exp, sizeof(exp), stdin) != NULL) {
        // Remove trailing newline
        int len = strlen(exp);
        if (len > 0 && exp[len-1] == '\n') {
            exp[len-1] = '\0';
        }
        
        int result = evaluatePostfix(exp);
        printf("%d\n", result);
    }
    
    return 0;
}
