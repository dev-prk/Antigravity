#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

void quicksort(int *arr, int low, int high) {
    if (low < high) {
        int pivot = *(arr + high);
        int i = low - 1;
        for (int j = low; j < high; j++) {
            if (*(arr + j) <= pivot) {
                i++;
                int temp = *(arr + i);
                *(arr + i) = *(arr + j);
                *(arr + j) = temp;
            }
        }
        int temp = *(arr + i + 1);
        *(arr + i + 1) = *(arr + high);
        *(arr + high) = temp;
        int pi = i + 1;
        
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}

int binary_search(int *arr, int n, int x) {
    int left = 0, right = n - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (*(arr + mid) == x) return mid;
        else if (*(arr + mid) < x) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    
    int *arr = (int*)malloc(n * sizeof(int));
    if (!arr) return 0;
    
    for (int i = 0; i < n; i++) {
        scanf("%d", arr + i);
    }
    
    int x;
    scanf("%d", &x);
    
    quicksort(arr, 0, n - 1);
    
    printf("Sorted array:");
    for (int i = 0; i < n; i++) {
        printf(" %d", *(arr + i));
    }
    printf(" \n");
    
    double median;
    if (n % 2 == 1) {
        median = *(arr + n / 2);
    } else {
        median = (*(arr + n / 2 - 1) + *(arr + n / 2)) / 2.0;
    }
    
    printf("Median: %.2f\n", median);
    
    int result = binary_search(arr, n, x);
    printf("Binary Search Result: %d\n", result);
    
    free(arr);
    return 0;
}
