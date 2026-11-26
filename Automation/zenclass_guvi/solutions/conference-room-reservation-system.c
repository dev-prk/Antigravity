#include <stdio.h>
#include <string.h>

int main() {
    int N;
    scanf("%d", &N);
    
    int reserved = 0;
    int current_employee = -1;
    char command[20];
    int employee_id;
    
    for (int i = 0; i < N; i++) {
        scanf("%s", command);
        
        if (strcmp(command, "RESERVE") == 0) {
            scanf("%d", &employee_id);
            
            if (reserved == 0) {
                reserved = 1;
                current_employee = employee_id;
                goto reserve_success;
            } else {
                goto reserve_already_reserved;
            }
        } else if (strcmp(command, "FREE") == 0) {
            scanf("%d", &employee_id);
            
            if (reserved == 0) {
                goto free_no_reservation;
            } else if (current_employee == employee_id) {
                reserved = 0;
                current_employee = -1;
                goto free_success;
            } else {
                goto free_mismatch;
            }
        }
        
        continue;
        
reserve_already_reserved:
        printf("Room Already Reserved by Employee %d\n", current_employee);
        continue;
        
reserve_success:
        printf("Room Reserved\n");
        continue;
        
free_success:
        printf("Room Freed\n");
        continue;
        
free_no_reservation:
        printf("No Reservation to Free\n");
        continue;
        
free_mismatch:
        printf("No Reservation to Free\n");
        continue;
    }
    
    return 0;
}
