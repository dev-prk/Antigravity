#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX 50

long long grid[MAX][MAX][MAX];
long long prefix[MAX][MAX][MAX];

long long getSum(int x1, int y1, int z1, int x2, int y2, int z2) {
    if (x1 > x2 || y1 > y2 || z1 > z2) return 0;
    long long sum = prefix[x2][y2][z2];
    if (x1 > 0) sum -= prefix[x1-1][y2][z2];
    if (y1 > 0) sum -= prefix[x2][y1-1][z2];
    if (z1 > 0) sum -= prefix[x2][y2][z1-1];
    if (x1 > 0 && y1 > 0) sum += prefix[x1-1][y1-1][z2];
    if (x1 > 0 && z1 > 0) sum += prefix[x1-1][y2][z1-1];
    if (y1 > 0 && z1 > 0) sum += prefix[x2][y1-1][z1-1];
    if (x1 > 0 && y1 > 0 && z1 > 0) sum -= prefix[x1-1][y1-1][z1-1];
    return sum;
}

int main() {
    int L, W, H;
    scanf("%d %d %d", &L, &W, &H);
    
    if (L <= 0 || W <= 0 || H <= 0) {
        printf("-1\n");
        return 0;
    }
    
    memset(grid, 0, sizeof(grid));
    memset(prefix, 0, sizeof(prefix));
    
    for (int x = 0; x < L; x++) {
        for (int y = 0; y < W; y++) {
            for (int z = 0; z < H; z++) {
                scanf("%lld", &grid[x][y][z]);
            }
        }
    }
    
    // Build 3D prefix sum
    for (int x = 0; x < L; x++) {
        for (int y = 0; y < W; y++) {
            for (int z = 0; z < H; z++) {
                prefix[x][y][z] = grid[x][y][z];
                if (x > 0) prefix[x][y][z] += prefix[x-1][y][z];
                if (y > 0) prefix[x][y][z] += prefix[x][y-1][z];
                if (z > 0) prefix[x][y][z] += prefix[x][y][z-1];
                if (x > 0 && y > 0) prefix[x][y][z] -= prefix[x-1][y-1][z];
                if (x > 0 && z > 0) prefix[x][y][z] -= prefix[x-1][y][z-1];
                if (y > 0 && z > 0) prefix[x][y][z] -= prefix[x][y-1][z-1];
                if (x > 0 && y > 0 && z > 0) prefix[x][y][z] += prefix[x-1][y-1][z-1];
            }
        }
    }
    
    long long maxSum = -1;
    int found = 0;
    
    // Try all possible sub-blocks
    for (int x1 = 0; x1 < L; x1++) {
        for (int x2 = x1; x2 < L; x2++) {
            for (int y1 = 0; y1 < W; y1++) {
                for (int y2 = y1; y2 < W; y2++) {
                    for (int z1 = 0; z1 < H; z1++) {
                        for (int z2 = z1; z2 < H; z2++) {
                            long long sum = getSum(x1, y1, z1, x2, y2, z2);
                            if (!found || sum > maxSum) {
                                maxSum = sum;
                                found = 1;
                            }
                        }
                    }
                }
            }
        }
    }
    
    if (!found) {
        printf("-1\n");
    } else {
        printf("%lld\n", maxSum);
    }
    
    return 0;
}
