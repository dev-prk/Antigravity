#include <stdio.h>
#include <string.h>

#define MAX_STUDENTS 100
#define NAME_LEN 51

typedef struct {
    char name[NAME_LEN];
    int roll_number;
    float marks1, marks2, marks3;
    float total;
    float average;
} Student;

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n < 1 || n > 100) {
        return 0;
    }

    Student students[MAX_STUDENTS];
    int count = 0;

    for (int i = 0; i < n; i++) {
        char newline[2];
        if (fgets(newline, 2, stdin) == NULL) break;

        if (fgets(students[i].name, NAME_LEN, stdin) == NULL) break;
        students[i].name[strcspn(students[i].name, "\n")] = '\0';

        if (scanf("%d", &students[i].roll_number) != 1) break;

        float m1, m2, m3;
        if (scanf("%f%f%f", &m1, &m2, &m3) != 3) break;

        students[i].marks1 = m1;
        students[i].marks2 = m2;
        students[i].marks3 = m3;
        students[i].total = m1 + m2 + m3;
        students[i].average = students[i].total / 3.0f;
        count++;
    }

    for (int i = 0; i < count - 1; i++) {
        for (int j = 0; j < count - i - 1; j++) {
            if (students[j].average < students[j + 1].average) {
                Student temp = students[j];
                students[j] = students[j + 1];
                students[j + 1] = temp;
            }
        }
    }

    if (count == 0) {
        printf("-1\n");
        return 0;
    }

    for (int i = 0; i < count; i++) {
        printf("Name: %s, Roll Number: %d, Total Marks: %.2f, Average Marks: %.2f\n",
               students[i].name,
               students[i].roll_number,
               students[i].total,
               students[i].average);
    }

    return 0;
}
