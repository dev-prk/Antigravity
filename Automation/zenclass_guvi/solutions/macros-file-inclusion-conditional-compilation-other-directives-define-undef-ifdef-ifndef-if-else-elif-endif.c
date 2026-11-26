#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MEMBERSHIP_BRONZE    1
#define MEMBERSHIP_SILVER    2
#define MEMBERSHIP_GOLD      3
#define MEMBERSHIP_PLATINUM  4

#define DISCOUNT_BRONZE     5.0f
#define DISCOUNT_SILVER    10.0f
#define DISCOUNT_GOLD      15.0f
#define DISCOUNT_PLATINUM  20.0f

int main(void) {
    double bill;
    int level;

    if (scanf("%lf", &bill) != 1) return 0;
    if (scanf("%d", &level) != 1) return 0;

    double discount;
    const char *membership;

#if MEMBERSHIP_BRONZE == 1
    #if MEMBERSHIP_SILVER == 2
        #if MEMBERSHIP_GOLD == 3
            #if MEMBERSHIP_PLATINUM == 4
                #define VALID_LEVELS 1
            #endif
        #endif
    #endif
#endif

    #ifdef VALID_LEVELS
    switch (level) {
        case MEMBERSHIP_BRONZE:
            discount = DISCOUNT_BRONZE;
            membership = "Bronze";
            break;
        case MEMBERSHIP_SILVER:
            discount = DISCOUNT_SILVER;
            membership = "Silver";
            break;
        case MEMBERSHIP_GOLD:
            discount = DISCOUNT_GOLD;
            membership = "Gold";
            break;
        case MEMBERSHIP_PLATINUM:
            discount = DISCOUNT_PLATINUM;
            membership = "Platinum";
            break;
        default:
            printf("Invalid membership level\n");
            return 0;
    }
    #else
    printf("Invalid configuration\n");
    return 0;
    #endif

    double final_price = bill * (1.0 - discount / 100.0);
    printf("%s Membership: %.0f%% Discount\n", membership, discount);
    printf("Final Price: %.2f\n", final_price);

    return 0;
}
