#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_SIZE 100005

int queue[MAX_SIZE];
int front, rear;
int size, capacity;

void init(int n) {
    capacity = n;
    size = 0;
    front = -1;
    rear = -1;
}

int is_empty() {
    return size == 0;
}

int is_full() {
    return size == capacity;
}

void enqueue(int x) {
    if (is_full()) {
        printf("Queue Overflow\n");
        return;
    }
    if (is_empty()) {
        front = 0;
        rear = 0;
    } else {
        rear = (rear + 1) % capacity;
    }
    queue[rear] = x;
    size++;
}

int dequeue() {
    if (is_empty()) {
        printf("Queue Underflow\n");
        return -1;
    }
    int val = queue[front];
    if (size == 1) {
        front = -1;
        rear = -1;
    } else {
        front = (front + 1) % capacity;
    }
    size--;
    return val;
}

void display() {
    if (is_empty()) {
        return;
    }
    int count = size;
    int idx = front;
    for (int i = 0; i < count; i++) {
        printf("%d", queue[idx]);
        if (i < count - 1) {
            printf(" ");
        }
        idx = (idx + 1) % capacity;
    }
    printf("\n");
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) {
        return 0;
    }
    
    init(n);
    
    char op[20];
    int x;
    
    while (scanf("%s", op) == 1) {
        if (strcmp(op, "enqueue") == 0) {
            if (scanf("%d", &x) == 1) {
                enqueue(x);
            }
        } else if (strcmp(op, "dequeue") == 0) {
            dequeue();
        } else if (strcmp(op, "display") == 0) {
            display();
        }
    }
    
    return 0;
}
