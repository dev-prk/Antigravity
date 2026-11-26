#include <stdio.h>
#include <stdlib.h>

#define MAX 100005

int stack[MAX];
int top = -1;

void push(int x) {
    stack[++top] = x;
}

int pop() {
    return stack[top--];
}

int main() {
    int queue[MAX];
    int n, k, i;
    
    scanf("%d", &n);
    
    for (i = 0; i < n; i++) {
        scanf("%d", &queue[i]);
    }
    
    scanf("%d", &k);
    
    // Handle edge cases
    if (k <= 0 || k > n) {
        // Print original queue if k is invalid
        for (i = 0; i < n; i++) {
            printf("%d", queue[i]);
            if (i < n - 1) printf(" ");
        }
        printf("\n");
        return 0;
    }
    
    // Push first k elements to stack
    for (i = 0; i < k; i++) {
        push(queue[i]);
    }
    
    // Pop from stack to get reversed order
    for (i = 0; i < k; i++) {
        queue[i] = pop();
    }
    
    // Print the modified queue
    for (i = 0; i < n; i++) {
        printf("%d", queue[i]);
        if (i < n - 1) printf(" ");
    }
    printf("\n");
    
    return 0;
}
