#include <stdio.h>
   #include <stdlib.h>
   #include <string.h>
   #include <math.h>

   int main() {
       int amount;
       if (scanf("%d", &amount) != 1) {
           return 1;
       }
       if (amount > 0) {
           printf("Deposit\n");
       } else if (amount < 0) {
           printf("Withdrawal\n");
       } else {
           printf("No Transaction\n");
       }
       return 0;
   }
