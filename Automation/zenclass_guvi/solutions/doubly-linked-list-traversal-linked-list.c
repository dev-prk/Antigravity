#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct Node {
    int data;
    struct Node* next;
    struct Node* prev;
} Node;

Node* createNode(int data) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (newNode == NULL) {
        return NULL;
    }
    newNode->data = data;
    newNode->next = NULL;
    newNode->prev = NULL;
    return newNode;
}

void insertAtEnd(Node** head, int data) {
    Node* newNode = createNode(data);
    if (newNode == NULL) {
        return;
    }
    
    if (*head == NULL) {
        *head = newNode;
        return;
    }
    
    Node* temp = *head;
    while (temp->next != NULL) {
        temp = temp->next;
    }
    
    temp->next = newNode;
    newNode->prev = temp;
}

void printForward(Node* head) {
    Node* current = head;
    int first = 1;
    while (current != NULL) {
        if (!first) {
            printf(" ");
        }
        printf("%d", current->data);
        first = 0;
        current = current->next;
    }
}

void printBackward(Node* tail) {
    Node* current = tail;
    int first = 1;
    while (current != NULL) {
        if (!first) {
            printf(" ");
        }
        printf("%d", current->data);
        first = 0;
        current = current->prev;
    }
}

void freeList(Node* head) {
    Node* current = head;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    
    Node* head = NULL;
    
    for (int i = 0; i < n; i++) {
        int data;
        if (scanf("%d", &data) == 1) {
            insertAtEnd(&head, data);
        }
    }
    
    printf("Forward: ");
    printForward(head);
    printf("\n");
    
    printf("Backward: ");
    Node* tail = head;
    if (tail != NULL) {
        while (tail->next != NULL) {
            tail = tail->next;
        }
    }
    printBackward(tail);
    printf("\n");
    
    freeList(head);
    
    return 0;
}
