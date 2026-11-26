#include <stdio.h>
#include <stdint.h>
#include <string.h>

void print_binary(uint32_t num) {
    char buffer[9];
    buffer[8] = '\0';
    for (int i = 7; i >= 0; i--) {
        buffer[7 - i] = (num & (1 << i)) ? '1' : '0';
    }
    printf("%s", buffer);
}

int main() {
    uint32_t userA, userB;
    scanf("%u %u", &userA, &userB);
    
    char op1[100], op2[100];
    scanf(" %99[^\n]", op1);
    scanf(" %99[^\n]", op2);
    
    // Grant Lights to User A (bit 0)
    userA = userA | 1;
    printf("User A Control Register after Granting Lights: %u\n", userA);
    
    // Revoke Music System from User B (bit 7)
    userB = userB & ~(1 << 7);
    printf("User B Control Register after Revoking Music System: %u\n", userB);
    
    // Check if User A has control over Cameras (bit 3)
    if (userA & (1 << 3)) {
        printf("User A has control over Cameras: Yes\n");
    } else {
        printf("User A has control over Cameras: No\n");
    }
    
    // Combine permissions
    uint32_t userC = userA | userB;
    printf("Combined Control Register (User C): %u\n", userC);
    
    // Print User A in binary
    printf("User A Control Register in Binary: ");
    print_binary(userA);
    printf("\n");
    
    return 0;
}
