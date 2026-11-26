#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node* left;
    struct Node* right;
};

struct Node* newNode(int data) {
    struct Node* node = (struct Node*)malloc(sizeof(struct Node));
    node->data = data;
    node->left = NULL;
    node->right = NULL;
    return node;
}

struct Node* buildTree(int* level, int n) {
    if (n == 0 || level[0] == -1) return NULL;
    
    struct Node* root = newNode(level[0]);
    struct Node* queue[1000];
    int front = 0, rear = 0;
    queue[rear++] = root;
    
    int i = 1;
    while (front < rear && i < n) {
        struct Node* current = queue[front++];
        
        if (i < n && level[i] != -1) {
            current->left = newNode(level[i]);
            queue[rear++] = current->left;
        }
        i++;
        
        if (i < n && level[i] != -1) {
            current->right = newNode(level[i]);
            queue[rear++] = current->right;
        }
        i++;
    }
    
    return root;
}

void postOrder(struct Node* root, int* result, int* index) {
    if (root == NULL) return;
    postOrder(root->left, result, index);
    postOrder(root->right, result, index);
    result[(*index)++] = root->data;
}

int main() {
    int n;
    scanf("%d", &n);
    
    int* level = (int*)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) {
        scanf("%d", &level[i]);
    }
    
    struct Node* root = buildTree(level, n);
    free(level);
    
    int* result = (int*)malloc(n * sizeof(int));
    int index = 0;
    postOrder(root, result, &index);
    
    for (int i = 0; i < index; i++) {
        if (i > 0) printf(" ");
        printf("%d", result[i]);
    }
    printf("\n");
    
    free(result);
    return 0;
}
