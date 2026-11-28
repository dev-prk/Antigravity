#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TOKEN 100

typedef struct {
    int *buffer;
    int capacity;
    int front;
    int rear;
    int count;
} CircularBuffer;

CircularBuffer* create_buffer(int initial_capacity) {
    CircularBuffer *cb = (CircularBuffer*)malloc(sizeof(CircularBuffer));
    if (!cb) return NULL;
    
    cb->buffer = (int*)malloc(initial_capacity * sizeof(int));
    if (!cb->buffer) {
        free(cb);
        return NULL;
    }
    
    cb->capacity = initial_capacity;
    cb->front = 0;
    cb->rear = -1;
    cb->count = 0;
    
    return cb;
}

void destroy_buffer(CircularBuffer *cb) {
    if (cb) {
        free(cb->buffer);
        free(cb);
    }
}

void print_buffer(CircularBuffer *cb) {
    if (cb->count == 0) {
        printf("\n");
        return;
    }
    
    for (int i = 0; i < cb->count; i++) {
        int index = (cb->front + i) % cb->capacity;
        printf("%d ", cb->buffer[index]);
    }
    printf("\n");
}

void add(CircularBuffer **cb, int value) {
    CircularBuffer *current = *cb;
    
    // If buffer is full, resize it
    if (current->count == current->capacity) {
        int new_capacity = current->capacity == 0 ? 1 : current->capacity * 2;
        int *new_buffer = (int*)realloc(current->buffer, new_capacity * sizeof(int));
        if (!new_buffer) return;
        
        // If front > rear, we need to rearrange
        if (current->front > current->rear) {
            int size = current->count;
            // Copy elements from front to end of old buffer
            for (int i = 0; i < size; i++) {
                new_buffer[i] = current->buffer[(current->front + i) % current->capacity];
            }
            current->front = 0;
            current->rear = size - 1;
        }
        
        current->buffer = new_buffer;
        current->capacity = new_capacity;
    }
    
    current->rear = (current->rear + 1) % current->capacity;
    current->buffer[current->rear] = value;
    current->count++;
}

void remove_element(CircularBuffer **cb) {
    CircularBuffer *current = *cb;
    
    if (current->count == 0) return;
    
    current->front = (current->front + 1) % current->capacity;
    current->count--;
}

void resize(CircularBuffer **cb, int new_size) {
    CircularBuffer *current = *cb;
    
    if (new_size <= 0) return;
    
    int *new_buffer = (int*)realloc(current->buffer, new_size * sizeof(int));
    if (!new_buffer) return;
    
    // Copy elements to new buffer starting from front
    int copy_count = (current->count < new_size) ? current->count : new_size;
    for (int i = 0; i < copy_count; i++) {
        new_buffer[i] = current->buffer[(current->front + i) % current->capacity];
    }
    
    current->buffer = new_buffer;
    current->capacity = new_size;
    current->front = 0;
    current->rear = copy_count - 1;
    current->count = copy_count;
}

int main() {
    int n;
    scanf("%d", &n);
    
    CircularBuffer *cb = create_buffer(1);
    
    char op[MAX_TOKEN];
    int val, new_size;
    
    for (int i = 0; i < n; i++) {
        scanf("%s", op);
        
        if (strcmp(op, "ADD") == 0) {
            scanf("%d", &val);
            add(&cb, val);
            print_buffer(cb);
        } else if (strcmp(op, "REMOVE") == 0) {
            remove_element(&cb);
            print_buffer(cb);
        } else if (strcmp(op, "RESIZE") == 0) {
            scanf("%d", &new_size);
            resize(&cb, new_size);
            print_buffer(cb);
        }
    }
    
    destroy_buffer(cb);
    return 0;
}
