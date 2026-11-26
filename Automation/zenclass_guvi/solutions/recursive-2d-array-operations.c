#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    long long sum;
    long long product;
    int count;
} Result;

Result recursive_ops(int *arr, int rows, int cols, int row, int col, int threshold) {
    Result res = {0, 1, 0};
    
    if (row >= rows) {
        return res;
    }
    
    int idx = row * cols + col;
    int val = arr[idx];
    
    Result next;
    if (col + 1 < cols) {
        next = recursive_ops(arr, rows, cols, row, col + 1, threshold);
    } else {
        next = recursive_ops(arr, rows, cols, row + 1, 0, threshold);
    }
    
    res.sum = val + next.sum;
    res.product = val * next.product;
    res.count = (val > threshold) ? 1 : 0;
    res.count += next.count;
    
    return res;
}

int main() {
    int rows, cols;
    if (scanf("%d %d", &rows, &cols) != 2) {
        return 1;
    }
    
    if (rows <= 0 || cols <= 0) {
        int threshold;
        scanf("%d", &threshold);
        printf("Sum: 0\n");
        printf("Product: 1\n");
        printf("Count greater than %d: 0\n", threshold);
        return 0;
    }
    
    int *arr = (int *)malloc(rows * cols * sizeof(int));
    if (arr == NULL) {
        return 1;
    }
    
    for (int i = 0; i < rows * cols; i++) {
        scanf("%d", &arr[i]);
    }
    
    int threshold;
    scanf("%d", &threshold);
    
    Result res = recursive_ops(arr, rows, cols, 0, 0, threshold);
    
    printf("Sum: %lld\n", res.sum);
    printf("Product: %lld\n", res.product);
    printf("Count greater than %d: %d\n", threshold, res.count);
    
    free(arr);
    return 0;
}
