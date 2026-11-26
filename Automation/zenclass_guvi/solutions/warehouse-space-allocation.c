#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int findMaxCapacity(int arr[], int n, int k) {
    if (n == 0 || k <= 0 || k > n) return -1;
    
    long long currentSum = 0;
    for (int i = 0; i < k; i++) {
        currentSum += arr[i];
    }
    
    long long maxSum = currentSum;
    int maxIndex = 0;
    
    for (int i = 1; i <= n - k; i++) {
        currentSum = currentSum - arr[i - 1] + arr[i + k - 1];
        if (currentSum > maxSum) {
            maxSum = currentSum;
            maxIndex = i;
        }
    }
    
    return maxIndex;
}

void getInputArray(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
}

int main() {
    int n, k;
    if (scanf("%d %d", &n, &k) != 2) {
        return 1;
    }
    
    if (n <= 0) {
        printf("-1\n");
        return 0;
    }
    
    int *arr = (int*)malloc(n * sizeof(int));
    if (arr == NULL) {
        printf("-1\n");
        return 1;
    }
    
    getInputArray(arr, n);
    
    int result = findMaxCapacity(arr, n, k);
    printf("%d\n", result);
    
    free(arr);
    return 0;
}
