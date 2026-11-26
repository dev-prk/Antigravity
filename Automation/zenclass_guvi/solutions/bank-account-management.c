#include <stdio.h>
#include <string.h>

struct Savings {
    float balance;
    float interestRate;
};

struct Checking {
    float balance;
    float overdraftLimit;
};

union AccountDetails {
    struct Savings savings;
    struct Checking checking;
};

struct BankAccount {
    char accountHolderName[100];
    int accountType;
    union AccountDetails details;
};

int main() {
    struct BankAccount account;
    
    fgets(account.accountHolderName, sizeof(account.accountHolderName), stdin);
    account.accountHolderName[strcspn(account.accountHolderName, "\n")] = '\0';
    
    scanf("%d", &account.accountType);
    
    if (account.accountType == 1) {
        scanf("%f %f", &account.details.savings.balance, &account.details.savings.interestRate);
        printf("Savings Account Balance: %.2f\n", account.details.savings.balance);
        printf("Annual Interest Rate: %.2f%%\n", account.details.savings.interestRate);
    } else if (account.accountType == 2) {
        scanf("%f %f", &account.details.checking.balance, &account.details.checking.overdraftLimit);
        printf("Checking Account Balance: %.2f\n", account.details.checking.balance);
        printf("Overdraft Limit: %.2f\n", account.details.checking.overdraftLimit);
    }
    
    return 0;
}
