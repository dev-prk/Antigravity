#include <stdio.h>
#include <stdlib.h>

#define BRONZE_DISCOUNT 5
#define SILVER_DISCOUNT 10
#define GOLD_DISCOUNT 15
#define PLATINUM_DISCOUNT 20

int main() {
    float amount, final_price;
    int level;
    
    scanf("%f", &amount);
    scanf("%d", &level);
    
    switch(level) {
        case 1:
            #ifdef BRONZE_DISCOUNT
            #undef BRONZE_DISCOUNT
            #define BRONZE_DISCOUNT 5
            #endif
            final_price = amount - (amount * BRONZE_DISCOUNT / 100.0);
            printf("Bronze Membership: %d%% Discount\n", BRONZE_DISCOUNT);
            break;
        case 2:
            #ifdef SILVER_DISCOUNT
            #undef SILVER_DISCOUNT
            #define SILVER_DISCOUNT 10
            #endif
            final_price = amount - (amount * SILVER_DISCOUNT / 100.0);
            printf("Silver Membership: %d%% Discount\n", SILVER_DISCOUNT);
            break;
        case 3:
            #ifdef GOLD_DISCOUNT
            #undef GOLD_DISCOUNT
            #define GOLD_DISCOUNT 15
            #endif
            final_price = amount - (amount * GOLD_DISCOUNT / 100.0);
            printf("Gold Membership: %d%% Discount\n", GOLD_DISCOUNT);
            break;
        case 4:
            #ifdef PLATINUM_DISCOUNT
            #undef PLATINUM_DISCOUNT
            #define PLATINUM_DISCOUNT 20
            #endif
            final_price = amount - (amount * PLATINUM_DISCOUNT / 100.0);
            printf("Platinum Membership: %d%% Discount\n", PLATINUM_DISCOUNT);
            break;
        default:
            final_price = amount;
            printf("Invalid Membership\n");
            break;
    }
    
    printf("Final Price: %.2f\n", final_price);
    
    return 0;
}
