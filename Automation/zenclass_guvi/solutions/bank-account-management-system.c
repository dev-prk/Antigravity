#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    float balance;
    float interestRate;
} Savings;

typedef struct {
    float balance;
    float overdraftLimit;
} Checking;

typedef union {
    Savings savings;
    Checking checking;
} AccountDetails;

typedef struct {
    char accountHolderName[100];
    int accountType;
    AccountDetails details;
} BankAccount;

int main() {
    BankAccount account;
    
    if (fgets(account.accountHolderName, sizeof(account.accountHolderName), stdin) != NULL) {
        size_t len = strlen(account.accountHolderName);
        if (len > 0 && account.accountHolderName[len - 1] == '\n') {
            account.accountHolderName[len - 1] = '\0';
        }
    }
    
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
