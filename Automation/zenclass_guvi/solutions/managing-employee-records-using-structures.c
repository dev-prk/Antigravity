#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    char name[101];
    int age;
    double salary;
} Employee;

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n <= 0) {
        return 0;
    }
    
    Employee *employees = (Employee *)malloc(n * sizeof(Employee));
    if (employees == NULL) {
        return 1;
    }
    
    for (int i = 0; i < n; i++) {
        scanf("%100s %d %lf", employees[i].name, &employees[i].age, &employees[i].salary);
    }
    
    for (int i = 0; i < n; i++) {
        printf("Name: %s, Age: %d, Salary: %.2f\n", employees[i].name, employees[i].age, employees[i].salary);
    }
    
    int max_idx = 0;
    for (int i = 1; i < n; i++) {
        if (employees[i].salary > employees[max_idx].salary) {
            max_idx = i;
        }
    }
    
    printf("Highest Salary -> Name: %s, Age: %d, Salary: %.2f\n", 
           employees[max_idx].name, employees[max_idx].age, employees[max_idx].salary);
    
    free(employees);
    return 0;
}
