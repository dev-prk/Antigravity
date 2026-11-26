#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
    int row;
    int col;
    int value;
    struct Node* next;
} Node;

Node* head = NULL;

void insert(int row, int col, int value) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->row = row;
    newNode->col = col;
    newNode->value = value;
    newNode->next = NULL;

    if (head == NULL || (row < head->row || (row == head->row && col < head->col))) {
        newNode->next = head;
        head = newNode;
        return;
    }

    Node* current = head;
    while (current->next != NULL && 
           (current->next->row < row || 
            (current->next->row == row && current->next->col < col))) {
        current = current->next;
    }

    if (current->row == row && current->col == col) {
        current->value = value;
        free(newNode);
    } else {
        newNode->next = current->next;
        current->next = newNode;
    }
}

void delete(int row, int col) {
    if (head == NULL) return;

    if (head->row == row && head->col == col) {
        Node* temp = head;
        head = head->next;
        free(temp);
        return;
    }

    Node* current = head;
    while (current->next != NULL && 
           !(current->next->row == row && current->next->col == col)) {
        current = current->next;
    }

    if (current->next != NULL && current->next->row == row && current->next->col == col) {
        Node* temp = current->next;
        current->next = current->next->next;
        free(temp);
    }
}

int retrieve(int row, int col) {
    Node* current = head;
    while (current != NULL) {
        if (current->row == row && current->col == col) {
            return current->value;
        }
        if (current->row > row || (current->row == row && current->col > col)) {
            break;
        }
        current = current->next;
    }
    return 0;
}

int main() {
    int n;
    scanf("%d", &n);

    char op[10];
    int row, col, value;

    for (int i = 0; i < n; i++) {
        scanf("%s", op);
        if (strcmp(op, "INSERT") == 0) {
            scanf("%d %d %d", &row, &col, &value);
            insert(row, col, value);
        } else if (strcmp(op, "DELETE") == 0) {
            scanf("%d %d", &row, &col);
            delete(row, col);
        } else if (strcmp(op, "RETRIEVE") == 0) {
            scanf("%d %d", &row, &col);
            printf("%d\n", retrieve(row, col));
        }
    }

    return 0;
}
