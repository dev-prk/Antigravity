#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main() {
    int balance;
    if (scanf("%d", &balance) != 1) {
        return 1;
    }
    
    char op[10];
    double value;
    
    while (scanf("%s", op) == 1) {
        if (op[0] == 'q') {
            break;
        }
        
        if (scanf("%lf", &value) != 1) {
            break;
        }
        
        switch(op[0]) {
            case '=':
                balance = (int)value;
                break;
            case '+':
                balance += (int)value;
                break;
            case '-':
                balance -= (int)value;
                break;
            case '*':
                balance = (int)(balance * value);
                break;
            case '/':
                if (value != 0) {
                    balance = (int)(balance / value);
                }
                break;
            case '%':
                if ((int)value != 0) {
                    balance %= (int)value;
                }
                break;
            case '&':
                balance &= (int)value;
                break;
            case '|':
                balance |= (int)value;
                break;
            case '^':
                balance ^= (int)value;
                break;
            case '<':
                if (op[1] == '<' && op[2] == '=') {
                    balance <<= (int)value;
                }
                break;
            case '>':
                if (op[1] == '>' && op[2] == '=') {
                    balance >>= (int)value;
                }
                break;
        }
    }
    
    printf("Final Balance: %d\n", balance);
    
    return 0;
}
