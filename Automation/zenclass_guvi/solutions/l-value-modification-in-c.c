#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(void) {
    int initial, heap_value;

    if (scanf("%d %d", &initial, &heap_value) != 2) {
        return 0;
    }

    int original = initial;
    int *ptr = &original;
    *ptr = *ptr + 5;

    int *heap_ptr = (int *)malloc(sizeof(int));
    if (heap_ptr == NULL) {
        return 1;
    }

    *heap_ptr = heap_value;

    printf("Original Integer: %d\n", original);
    printf("Heap Integer: %d\n", *heap_ptr);

    free(heap_ptr);
    return 0;
}
