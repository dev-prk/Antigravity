#include <iostream>
#include <string>
using namespace std;

class Student {
private:
    string name;
    int marks;
public:
    void input() {
        cin >> name >> marks;
    }
    
    void display() {
        cout << "Name: " << name << ", Marks: " << marks << endl;
    }
    
    static double calculateAverage(Student* arr[], int n) {
        double sum = 0;
        for (int i = 0; i < n; i++) {
            sum += arr[i]->marks;
        }
        return sum / n;
    }
};

int main() {
    int n;
    cin >> n;
    
    Student** students = new Student*[n];
    
    for (int i = 0; i < n; i++) {
        students[i] = new Student();
        students[i]->input();
    }
    
    cout << "Student Details:" << endl;
    for (int i = 0; i < n; i++) {
        students[i]->display();
    }
    
    double avg = Student::calculateAverage(students, n);
    cout << "Average Marks: " << (int)avg << endl;
    
    for (int i = 0; i < n; i++) {
        delete students[i];
    }
    delete[] students;
    
    return 0;
}
