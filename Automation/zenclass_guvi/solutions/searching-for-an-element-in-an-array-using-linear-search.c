#include <stdio.h>
int main(void) {
    int N;
    if (scanf("%d", &N) != 1) return 0;
    
    int arr[N];
    for (int i = 0; i < N; i++) {
        scanf("%d", &arr[i]);
    }
    
    int key;
    scanf("%d", &key);
    
    int found = -1;
    for (int i = 0; i < N; i++) {
        if (arr[i] == key) {
            found = i;
            break;
        }
    }
    
    if (found != -1) {
        printf("%d\n", found);
    } else {
        printf("Not Found\n");
    }
    
    return 0;
}
