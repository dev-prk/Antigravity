#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* createNode(int data) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (newNode == NULL) {
        return NULL;
    }
    newNode->data = data;
    newNode->next = NULL;
    return newNode;
}

int detectCycle(Node* head) {
    if (head == NULL || head->next == NULL) {
        return 0;
    }
    
    Node* slow = head;
    Node* fast = head;
    
    while (fast != NULL && fast->next != NULL) {
        slow = slow->next;
        fast = fast->next->next;
        
        if (slow == fast) {
            return 1;
        }
    }
    
    return 0;
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    if (n <= 0) {
        int pos;
        scanf("%d", &pos);
        printf("No Cycle\n");
        return 0;
    }
    
    Node* head = NULL;
    Node* tail = NULL;
    Node* nodes[100000];
    int nodeCount = 0;
    
    for (int i = 0; i < n; i++) {
        int val;
        scanf("%d", &val);
        Node* newNode = createNode(val);
        nodes[nodeCount++] = newNode;
        
        if (head == NULL) {
            head = newNode;
            tail = newNode;
        } else {
            tail->next = newNode;
            tail = newNode;
        }
    }
    
    int pos;
    scanf("%d", &pos);
    
    if (pos >= 0 && pos < n) {
        tail->next = nodes[pos];
    }
    
    if (detectCycle(head)) {
        printf("Cycle Found\n");
    } else {
        printf("No Cycle\n");
    }
    
    return 0;
}
