#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct ListNode {
    int val;
    struct ListNode* next;
} ListNode;

typedef struct {
    ListNode* node;
} HeapNode;

int compare(const void* a, const void* b) {
    HeapNode* nodeA = (HeapNode*)a;
    HeapNode* nodeB = (HeapNode*)b;
    return nodeA->node->val - nodeB->node->val;
}

void heapifyUp(HeapNode* heap, int size, int idx) {
    while (idx > 0) {
        int parent = (idx - 1) / 2;
        if (heap[idx].node->val >= heap[parent].node->val) break;
        HeapNode temp = heap[idx];
        heap[idx] = heap[parent];
        heap[parent] = temp;
        idx = parent;
    }
}

void heapifyDown(HeapNode* heap, int size, int idx) {
    while (1) {
        int smallest = idx;
        int left = 2 * idx + 1;
        int right = 2 * idx + 2;
        
        if (left < size && heap[left].node->val < heap[smallest].node->val) {
            smallest = left;
        }
        if (right < size && heap[right].node->val < heap[smallest].node->val) {
            smallest = right;
        }
        if (smallest == idx) break;
        
        HeapNode temp = heap[idx];
        heap[idx] = heap[smallest];
        heap[smallest] = temp;
        idx = smallest;
    }
}

void push(HeapNode** heap, int* size, ListNode* node) {
    HeapNode* newHeap = realloc(*heap, (*size + 1) * sizeof(HeapNode));
    if (!newHeap) exit(1);
    *heap = newHeap;
    (*heap)[*size].node = node;
    heapifyUp(*heap, *size + 1, *size);
    (*size)++;
}

ListNode* pop(HeapNode** heap, int* size) {
    if (*size == 0) return NULL;
    ListNode* minNode = (*heap)[0].node;
    (*heap)[0] = (*heap)[*size - 1];
    (*size)--;
    heapifyDown(*heap, *size, 0);
    return minNode;
}

ListNode* createList(int* arr, int n) {
    if (n == 0) return NULL;
    ListNode* head = malloc(sizeof(ListNode));
    head->val = arr[0];
    head->next = NULL;
    ListNode* curr = head;
    for (int i = 1; i < n; i++) {
        curr->next = malloc(sizeof(ListNode));
        curr = curr->next;
        curr->val = arr[i];
        curr->next = NULL;
    }
    return head;
}

ListNode* mergeKLists(ListNode** lists, int k) {
    HeapNode* heap = NULL;
    int heapSize = 0;
    
    for (int i = 0; i < k; i++) {
        if (lists[i] != NULL) {
            push(&heap, &heapSize, lists[i]);
        }
    }
    
    if (heapSize == 0) {
        free(heap);
        return NULL;
    }
    
    ListNode* merged = pop(&heap, &heapSize);
    ListNode* tail = merged;
    
    if (merged->next != NULL) {
        push(&heap, &heapSize, merged->next);
    }
    
    while (heapSize > 0) {
        ListNode* minNode = pop(&heap, &heapSize);
        tail->next = minNode;
        tail = minNode;
        if (minNode->next != NULL) {
            push(&heap, &heapSize, minNode->next);
        }
    }
    
    tail->next = NULL;
    free(heap);
    return merged;
}

void printList(ListNode* head) {
    ListNode* curr = head;
    while (curr != NULL) {
        printf("%d", curr->val);
        if (curr->next != NULL) printf(" ");
        curr = curr->next;
    }
    printf("\n");
}

void freeList(ListNode* head) {
    while (head != NULL) {
        ListNode* temp = head;
        head = head->next;
        free(temp);
    }
}

int main() {
    int K;
    if (scanf("%d", &K) != 1) return 0;
    
    ListNode** lists = malloc(K * sizeof(ListNode*));
    
    for (int i = 0; i < K; i++) {
        int N;
        scanf("%d", &N);
        int* arr = malloc(N * sizeof(int));
        for (int j = 0; j < N; j++) {
            scanf("%d", &arr[j]);
        }
        lists[i] = createList(arr, N);
        free(arr);
    }
    
    ListNode* merged = mergeKLists(lists, K);
    free(lists);
    
    printList(merged);
    freeList(merged);
    
    return 0;
}
