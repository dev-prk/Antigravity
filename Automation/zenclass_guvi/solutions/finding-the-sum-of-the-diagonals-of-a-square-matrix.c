#include <stdio.h>
int main(void) {
    int N;
    scanf("%d", &N);
    long long main_diag = 0, sec_diag = 0;
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            int val;
            scanf("%d", &val);
            if (j == i) main_diag += val;
            if (j == N - 1 - i) sec_diag += val;
        }
    }
    printf("%lld\n%lld\n", main_diag, sec_diag);
    return 0;
}
