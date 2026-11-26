#include <stdio.h>
int main(void) {
    int m1, m2, m3, w1, w2, w3;
    scanf("%d %d %d %d %d %d", &m1, &m2, &m3, &w1, &w2, &w3);

    // Compute weighted sum using compound assignment
    int weightedSum = 0;
    weightedSum += m1 * w1;
    weightedSum += m2 * w2;
    weightedSum += m3 * w3;

    // Compute total weight
    int weightSum = w1 + w2 + w3;

    // Compute weighted average with explicit casting to float
    float average = (float)weightedSum / (float)weightSum;

    // Print with two decimal places
    printf("%.2f\n", average);

    return 0;
}
