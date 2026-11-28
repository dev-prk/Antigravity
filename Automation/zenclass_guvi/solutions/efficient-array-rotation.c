#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

void reverse(int arr[], int start, int end) {
    while (start < end) {
        int temp = arr[start];
        arr[start] = arr[end];
        arr[end] = temp;
        start++;
        end--;
    }
}

void rotateArray(int arr[], int n, int d, char dir) {
    if (d == 0 || n == 1) {
        return;
    }
    
    if (dir == 'R') {
        d = n - d;
    }
    
    reverse(arr, 0, d - 1);
    reverse(arr, d, n - 1);
    reverse(arr, 0, n - 1);
}

int main() {
    int n, d;
    if (scanf("%d %d", &n, &d) != 2) {
        return 1;
    }
    
    int *arr = (int*)malloc(n * sizeof(int));
    if (arr == NULL) {
        return 1;
    }
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    char dir;
    scanf(" %c", &dir);
    
    rotateArray(arr, n, d, dir);
    
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    
    free(arr);
    return 0;
}
