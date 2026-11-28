#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int compare(const void *a, const void *b) {
    return (*(int*)a - *(int*)b);
}

int binary_search(int *arr, int n, int x) {
    int *left = arr;
    int *right = arr + n - 1;
    
    while (left <= right) {
        int *mid = left + (right - left) / 2;
        if (*mid == x) {
            return (int)(mid - arr);
        } else if (*mid < x) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    int *arr = (int*)malloc(n * sizeof(int));
    if (arr == NULL) return 0;
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    int x;
    scanf("%d", &x);
    
    qsort(arr, n, sizeof(int), compare);
    
    // Print sorted array with space after each element and trailing space
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    
    // Print median with 2 decimal places
    double median;
    if (n % 2 == 1) {
        median = (double)arr[n / 2];
    } else {
        median = (double)(arr[n / 2 - 1] + arr[n / 2]) / 2.0;
    }
    printf("%.2f\n", median);
    
    // Print binary search result
    int result = binary_search(arr, n, x);
    printf("%d\n", result);
    
    free(arr);
    return 0;
}
