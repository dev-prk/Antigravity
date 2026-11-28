#include <stdio.h>
#include <stdlib.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    int *original = (int *)malloc(n * sizeof(int));
    if (original == NULL) return 0;
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &original[i]);
    }
    
    // Print original array
    printf("Original array:");
    for (int i = 0; i < n; i++) {
        printf(" %d", original[i]);
    }
    printf(" \n");
    
    // Create doubled array
    int new_size = n * 2;
    int *copied = (int *)malloc(new_size * sizeof(int));
    if (copied == NULL) {
        free(original);
        return 0;
    }
    
    // Copy original to copied
    for (int i = 0; i < n; i++) {
        copied[i] = original[i];
    }
    
    // Fill rest with zeros
    for (int i = n; i < new_size; i++) {
        copied[i] = 0;
    }
    
    // Print copied array
    printf("Copied array:");
    for (int i = 0; i < new_size; i++) {
        printf(" %d", copied[i]);
    }
    printf(" \n");
    
    // Free memory
    free(original);
    free(copied);
    
    return 0;
}
