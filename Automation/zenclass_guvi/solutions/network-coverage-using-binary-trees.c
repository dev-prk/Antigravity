#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct Node {
    int data;
    struct Node *left, *right;
} Node;

Node* newNode(int data) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->data = data;
    node->left = node->right = NULL;
    return node;
}

Node* insert(Node* root, int data) {
    if (root == NULL) return newNode(data);
    if (data < root->data)
        root->left = insert(root->left, data);
    else if (data > root->data)
        root->right = insert(root->right, data);
    return root;
}

Node* minValueNode(Node* root) {
    Node* current = root;
    while (current && current->left != NULL)
        current = current->left;
    return current;
}

Node* deleteNode(Node* root, int data) {
    if (root == NULL) return root;
    if (data < root->data)
        root->left = deleteNode(root->left, data);
    else if (data > root->data)
        root->right = deleteNode(root->right, data);
    else {
        if (root->left == NULL) {
            Node* temp = root->right;
            free(root);
            return temp;
        } else if (root->right == NULL) {
            Node* temp = root->left;
            free(root);
            return temp;
        }
        Node* temp = minValueNode(root->right);
        root->data = temp->data;
        root->right = deleteNode(root->right, temp->data);
    }
    return root;
}

int findMin(Node* root) {
    if (root == NULL) return -1;
    while (root->left != NULL)
        root = root->left;
    return root->data;
}

int findMax(Node* root) {
    if (root == NULL) return -1;
    while (root->right != NULL)
        root = root->right;
    return root->data;
}

int find(Node* root, int data) {
    if (root == NULL) return 0;
    if (root->data == data) return 1;
    if (data < root->data) return find(root->left, data);
    return find(root->right, data);
}

void inOrder(Node* root, int* result, int* index) {
    if (root == NULL) return;
    inOrder(root->left, result, index);
    result[(*index)++] = root->data;
    inOrder(root->right, result, index);
}

void printInOrder(Node* root) {
    if (root == NULL) {
        printf("\n");
        return;
    }
    // Count nodes first
    int count = 0;
    Node* stack[1000];
    int top = -1;
    Node* curr = root;
    while (curr != NULL || top >= 0) {
        while (curr != NULL) {
            stack[++top] = curr;
            curr = curr->left;
        }
        curr = stack[top--];
        count++;
        curr = curr->right;
    }
    
    int* result = (int*)malloc(count * sizeof(int));
    int index = 0;
    inOrder(root, result, &index);
    
    for (int i = 0; i < count; i++) {
        printf("%d", result[i]);
        if (i < count - 1) printf(" ");
    }
    printf("\n");
    free(result);
}

int main() {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    Node* root = NULL;
    
    char op[20];
    int val;
    
    for (int i = 0; i < N; i++) {
        scanf("%s", op);
        
        if (strcmp(op, "INSERT") == 0) {
            scanf("%d", &val);
            root = insert(root, val);
        } else if (strcmp(op, "DELETE") == 0) {
            scanf("%d", &val);
            if (find(root, val)) {
                root = deleteNode(root, val);
            } else {
                printf("Tower not found\n");
            }
        } else if (strcmp(op, "MIN") == 0) {
            int minVal = findMin(root);
            if (minVal != -1)
                printf("%d\n", minVal);
        } else if (strcmp(op, "MAX") == 0) {
            int maxVal = findMax(root);
            if (maxVal != -1)
                printf("%d\n", maxVal);
        } else if (strcmp(op, "FIND") == 0) {
            scanf("%d", &val);
            if (find(root, val))
                printf("Found\n");
            else
                printf("Not Found\n");
        } else if (strcmp(op, "PRINT") == 0) {
            printInOrder(root);
        }
    }
    
    return 0;
}
