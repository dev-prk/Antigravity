#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NAME_LEN 100

typedef struct {
    char name[MAX_NAME_LEN];
    int salary;
} Employee;

Employee *employees;
int emp_count = 0;

void swap(Employee *a, Employee *b) {
    Employee temp = *a;
    *a = *b;
    *b = temp;
}

int compare(Employee a, Employee b) {
    if (a.salary != b.salary) {
        return a.salary > b.salary ? 1 : 0;
    }
    return strcmp(a.name, b.name) < 0;
}

int partition(int low, int high) {
    Employee pivot = employees[high];
    int i = low - 1;
    
    for (int j = low; j < high; j++) {
        if (compare(employees[j], pivot)) {
            i++;
            swap(&employees[i], &employees[j]);
        }
    }
    swap(&employees[i + 1], &employees[high]);
    return i + 1;
}

void quickSort(int low, int high) {
    if (low < high) {
        int pi = partition(low, high);
        quickSort(low, pi - 1);
        quickSort(pi + 1, high);
    }
}

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n <= 0) {
        return 0;
    }
    
    employees = (Employee *)malloc(n * sizeof(Employee));
    if (employees == NULL) {
        return 1;
    }
    
    for (int i = 0; i < n; i++) {
        scanf("%s %d", employees[i].name, &employees[i].salary);
    }
    
    quickSort(0, n - 1);
    
    for (int i = 0; i < n; i++) {
        printf("%s %d\n", employees[i].name, employees[i].salary);
    }
    
    free(employees);
    return 0;
}
