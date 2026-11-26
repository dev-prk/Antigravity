#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    
    int *employee_ids = (int *)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) {
        scanf("%d", &employee_ids[i]);
    }
    
    int m;
    scanf("%d", &m);
    
    int *weights = (int *)malloc(m * sizeof(int));
    for (int i = 0; i < m; i++) {
        scanf("%d", &weights[i]);
    }
    
    int **ratings = (int **)malloc(n * sizeof(int *));
    for (int emp = 0; emp < n; emp++) {
        ratings[emp] = (int *)malloc(m * sizeof(int));
        for (int proj = 0; proj < m; proj++) {
            scanf("%d", &ratings[emp][proj]);
        }
    }
    
    for (int emp = 0; emp < n; emp++) {
        int total_score = 0;
        for (int proj = 0; proj < m; proj++) {
            total_score += ratings[emp][proj] * weights[proj];
        }
        printf("Employee ID %d has a total score of %d\n", employee_ids[emp], total_score);
    }
    
    for (int i = 0; i < n; i++) {
        free(ratings[i]);
    }
    free(ratings);
    free(weights);
    free(employee_ids);
    
    return 0;
}
