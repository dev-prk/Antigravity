#include <stdio.h>
#include <stdlib.h>

int compare(const void *a, const void *b) {
    return (*(int*)a - *(int*)b);
}

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n <= 0) {
        printf("-1\n");
        return 0;
    }
    
    int *files = (int*)malloc(n * sizeof(int));
    if (files == NULL) {
        printf("-1\n");
        return 0;
    }
    
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &files[i]) != 1) {
            free(files);
            printf("-1\n");
            return 0;
        }
    }
    
    if (n == 1) {
        free(files);
        printf("0\n");
        return 0;
    }
    
    qsort(files, n, sizeof(int), compare);
    
    long long total_cost = 0;
    int size = n;
    
    while (size > 1) {
        int sum = files[0] + files[1];
        total_cost += sum;
        
        for (int i = 0; i < size - 2; i++) {
            files[i] = files[i + 2];
        }
        files[size - 2] = sum;
        size--;
        
        int j = size - 1;
        while (j > 0 && files[j - 1] > files[j]) {
            int temp = files[j];
            files[j] = files[j - 1];
            files[j - 1] = temp;
            j--;
        }
    }
    
    free(files);
    printf("%lld\n", total_cost);
    return 0;
}
