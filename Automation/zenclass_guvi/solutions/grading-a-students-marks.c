#include <stdio.h>
int main(void) {
    int marks;
    char grade;
    scanf("%d", &marks);
    if (marks >= 90) {
        grade = 'A';
    } else if (marks >= 75) {
        grade = 'B';
    } else if (marks >= 60) {
        grade = 'C';
    } else if (marks >= 40) {
        grade = 'D';
    } else {
        grade = 'F';
    }
    printf("%c\n", grade);
    return 0;
}
