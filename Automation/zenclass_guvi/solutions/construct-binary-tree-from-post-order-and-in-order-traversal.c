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

int inOrderIndex(int in[], int start, int end, int value) {
    for (int i = start; i <= end; i++) {
        if (in[i] == value) return i;
    }
    return -1;
}

Node* buildHelper(int in[], int inStart, int inEnd, int post[], int postStart, int postEnd) {
    if (postStart > postEnd) return NULL;
    
    int rootValue = post[postEnd];
    Node* root = newNode(rootValue);
    
    if (inStart == inEnd) {
        return root;
    }
    
    int inRootIndex = inOrderIndex(in, inStart, inEnd, rootValue);
    
    int leftSubtreeSize = inRootIndex - inStart;
    
    root->left = buildHelper(in, inStart, inRootIndex - 1,
                             post, postStart, postStart + leftSubtreeSize - 1);
    root->right = buildHelper(in, inRootIndex + 1, inEnd,
                              post, postStart + leftSubtreeSize, postEnd - 1);
    
    return root;
}

Node* buildTree(int in[], int post[], int n) {
    if (n == 0) return NULL;
    return buildHelper(in, 0, n - 1, post, 0, n - 1);
}

void preOrder(Node* root, int* result, int* index) {
    if (root == NULL) return;
    result[(*index)++] = root->data;
    preOrder(root->left, result, index);
    preOrder(root->right, result, index);
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    if (n == 0) {
        printf("-1\n");
        return 0;
    }
    
    int* inOrder = (int*)malloc(n * sizeof(int));
    int* postOrder = (int*)malloc(n * sizeof(int));
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &inOrder[i]);
    }
    for (int i = 0; i < n; i++) {
        scanf("%d", &postOrder[i]);
    }
    
    Node* root = buildTree(inOrder, postOrder, n);
    
    int* preResult = (int*)malloc(n * sizeof(int));
    int index = 0;
    preOrder(root, preResult, &index);
    
    for (int i = 0; i < n; i++) {
        printf("%d", preResult[i]);
        if (i < n - 1) printf(" ");
    }
    printf("\n");
    
    free(inOrder);
    free(postOrder);
    free(preResult);
    
    return 0;
}
