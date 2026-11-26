#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    int num;
    int denom;
} Fraction;

Fraction* merge(Fraction* left, int leftSize, Fraction* right, int rightSize, Fraction* temp) {
    int i = 0, j = 0, k = 0;
    
    while (i < leftSize && j < rightSize) {
        double leftVal = (double)left[i].num / left[i].denom;
        double rightVal = (double)right[j].num / right[j].denom;
        
        if (leftVal <= rightVal) {
            temp[k++] = left[i++];
        } else {
            temp[k++] = right[j++];
        }
    }
    
    while (i < leftSize) {
        temp[k++] = left[i++];
    }
    
    while (j < rightSize) {
        temp[k++] = right[j++];
    }
    
    return temp;
}

void merge_sort(Fraction* arr, int n, Fraction* temp) {
    if (n <= 1) return;
    
    int mid = n / 2;
    Fraction* left = (Fraction*)malloc(mid * sizeof(Fraction));
    Fraction* right = (Fraction*)malloc((n - mid) * sizeof(Fraction));
    
    for (int i = 0; i < mid; i++) {
        left[i] = arr[i];
    }
    for (int i = mid; i < n; i++) {
        right[i - mid] = arr[i];
    }
    
    merge_sort(left, mid, temp);
    merge_sort(right, n - mid, temp);
    
    Fraction* result = merge(left, mid, right, n - mid, temp);
    for (int i = 0; i < n; i++) {
        arr[i] = result[i];
    }
    
    free(left);
    free(right);
}

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n <= 0) {
        return 0;
    }
    
    Fraction* fractions = (Fraction*)malloc(n * sizeof(Fraction));
    Fraction* temp = (Fraction*)malloc(n * sizeof(Fraction));
    
    for (int i = 0; i < n; i++) {
        scanf("%d %d", &fractions[i].num, &fractions[i].denom);
    }
    
    merge_sort(fractions, n, temp);
    
    for (int i = 0; i < n; i++) {
        printf("%d/%d\n", fractions[i].num, fractions[i].denom);
    }
    
    free(fractions);
    free(temp);
    
    return 0;
}
