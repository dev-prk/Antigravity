#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    if (N <= 0) {
        return 0;
    }
    
    int *arr = (int *)calloc(N, sizeof(int));
    if (arr == NULL) return 0;
    
    for (int i = 0; i < N; i++) {
        scanf("%d", &arr[i]);
    }
    
    // Calculate the size needed for frequency array
    // Elements range from -10000 to 10000
    int min_val = -10000;
    int max_val = 10000;
    int offset = 10000; // To handle negative indices
    int freq_size = max_val - min_val + 1;
    
    int *freq = (int *)calloc(freq_size, sizeof(int));
    if (freq == NULL) {
        free(arr);
        return 0;
    }
    
    // Count frequencies
    for (int i = 0; i < N; i++) {
        freq[arr[i] + offset]++;
    }
    
    // Track which elements we've seen (for order of first occurrence)
    int *seen = (int *)calloc(N, sizeof(int));
    if (seen == NULL) {
        free(arr);
        free(freq);
        return 0;
    }
    
    // Track which elements are active in output
    int *is_active = (int *)calloc(freq_size, sizeof(int));
    if (is_active == NULL) {
        free(arr);
        free(freq);
        free(seen);
        return 0;
    }
    
    // Process elements in order of first occurrence
    int print_count = 0;
    for (int i = 0; i < N; i++) {
        if (seen[i] == 0) {
            seen[i] = 1;
            int val = arr[i];
            int idx = val + offset;
            
            if (is_active[idx] == 0) {
                // Mark as active and print
                is_active[idx] = 1;
                if (print_count > 0) {
                    printf("\n");
                }
                print_count++;
                printf("%d %d", val, freq[idx]);
            }
        }
    }
    
    printf("\n");
    
    // Free all allocated memory
    free(arr);
    free(freq);
    free(seen);
    free(is_active);
    
    return 0;
}
