#include <stdio.h>
int main(void) {
    int m, n;
    scanf("%d %d", &m, &n);
    int sum = 0;
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            int val;
            scanf("%d", &val);
            sum += val;
        }
    }
    printf("%d\n", sum);
    return 0;
}
