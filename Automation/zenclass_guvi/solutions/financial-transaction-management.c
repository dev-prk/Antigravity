#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    float amount;
    int account_number;
    char atm_location[256];
} DepositWithdrawalData;

typedef struct {
    float amount;
    int from_account;
    int to_account;
} TransferData;

typedef struct {
    char type;
    union {
        DepositWithdrawalData dw_data;
        TransferData t_data;
    } data;
} Transaction;

int main() {
    Transaction trans;
    char type_char;
    char buffer[256];
    
    if (scanf(" %c", &type_char) != 1) {
        return 1;
    }
    trans.type = type_char;
    
    if (trans.type == 'D') {
        if (scanf("%f", &trans.data.dw_data.amount) != 1) {
            return 1;
        }
        if (scanf("%d", &trans.data.dw_data.account_number) != 1) {
            return 1;
        }
        printf("Transaction Type: Deposit\n");
        printf("Amount: %.2f\n", trans.data.dw_data.amount);
        printf("Account Number: %d\n", trans.data.dw_data.account_number);
    }
    else if (trans.type == 'W') {
        if (scanf("%f", &trans.data.dw_data.amount) != 1) {
            return 1;
        }
        if (scanf("%d", &trans.data.dw_data.account_number) != 1) {
            return 1;
        }
        // Clear any remaining input before reading the ATM location line
        int c;
        while ((c = getchar()) != '\n' && c != EOF);
        if (fgets(trans.data.dw_data.atm_location, sizeof(trans.data.dw_data.atm_location), stdin) != NULL) {
            // Remove trailing newline
            size_t len = strlen(trans.data.dw_data.atm_location);
            if (len > 0 && trans.data.dw_data.atm_location[len-1] == '\n') {
                trans.data.dw_data.atm_location[len-1] = '\0';
            }
            // Remove trailing spaces
            while (len > 0 && trans.data.dw_data.atm_location[len-1] == ' ') {
                trans.data.dw_data.atm_location[--len] = '\0';
            }
        }
        printf("Transaction Type: Withdrawal\n");
        printf("Amount: %.2f\n", trans.data.dw_data.amount);
        printf("Account Number: %d\n", trans.data.dw_data.account_number);
        printf("ATM Location: %s\n", trans.data.dw_data.atm_location);
    }
    else if (trans.type == 'T') {
        if (scanf("%f", &trans.data.t_data.amount) != 1) {
            return 1;
        }
        if (scanf("%d", &trans.data.t_data.from_account) != 1) {
            return 1;
        }
        if (scanf("%d", &trans.data.t_data.to_account) != 1) {
            return 1;
        }
        printf("Transaction Type: Transfer\n");
        printf("Amount: %.2f\n", trans.data.t_data.amount);
        printf("From Account Number: %d\n", trans.data.t_data.from_account);
        printf("To Account Number: %d\n", trans.data.t_data.to_account);
    }
    
    return 0;
}
