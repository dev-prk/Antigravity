#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Node {
    int data;
    struct Node* next;
};

typedef struct Node Node;

Node* head = NULL;

void insert(int x) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->data = x;
    newNode->next = NULL;
    
    if (head == NULL) {
        head = newNode;
    } else {
        Node* temp = head;
        while (temp->next != NULL) {
            temp = temp->next;
        }
        temp->next = newNode;
    }
}

void deleteValue(int x) {
    Node* current = head;
    Node* prev = NULL;
    
    while (current != NULL) {
        if (current->data == x) {
            if (prev == NULL) {
                head = current->next;
                free(current);
                current = head;
            } else {
                prev->next = current->next;
                free(current);
                current = prev->next;
            }
        } else {
            prev = current;
            current = current->next;
        }
    }
}

void reverse() {
    Node* prev = NULL;
    Node* current = head;
    Node* next = NULL;
    
    while (current != NULL) {
        next = current->next;
        current->next = prev;
        prev = current;
        current = next;
    }
    
    head = prev;
}

void printList() {
    if (head == NULL) {
        printf("EMPTY\n");
    } else {
        Node* temp = head;
        while (temp != NULL) {
            printf("%d", temp->data);
            if (temp->next != NULL) {
                printf(" ");
            }
            temp = temp->next;
        }
        printf("\n");
    }
}

int main() {
    int Q;
    scanf("%d", &Q);
    
    char operation[20];
    int x;
    
    for (int i = 0; i < Q; i++) {
        scanf("%s", operation);
        
        if (strcmp(operation, "INSERT") == 0) {
            scanf("%d", &x);
            insert(x);
        } else if (strcmp(operation, "DELETE") == 0) {
            scanf("%d", &x);
            deleteValue(x);
        } else if (strcmp(operation, "REVERSE") == 0) {
            reverse();
        }
    }
    
    printList();
    
    return 0;
}
